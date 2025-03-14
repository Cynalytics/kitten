from functools import wraps
from typing import Any
from collections.abc import Callable
import typing
import structlog
from httpx import Client, HTTPTransport, HTTPStatusError, ConnectError

from kitten.models.api_models import LuikPopRequest, LuikPopResponse

logger = structlog.get_logger(__name__)

ClientSessionMethod = Callable[..., Any]


def retry_with_login(function: ClientSessionMethod) -> ClientSessionMethod:
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except HTTPStatusError as error:
            if error.response.status_code != 401:
                raise

            self.login()
            return function(self, *args, **kwargs)

    return typing.cast(ClientSessionMethod, wrapper)


class LuikClientInterface:
    def pop_queue(
        self, task_capabilities: list[str], reachable_networks: list[str]
    ) -> LuikPopResponse | None:
        raise NotImplementedError()


class LuikClient(LuikClientInterface):
    def __init__(self, base_url: str, queue: str, auth_password: str):
        self.session = Client(base_url=base_url, transport=HTTPTransport(retries=3))
        self._queue = queue
        self._auth_password = auth_password

    def login(self) -> None:
        auth_header = {"Authorization": f"Bearer {self._get_token()}"}
        self.session.headers.update(auth_header)

    def _get_token(self) -> str:
        response = self.session.post(
            "/token",
            data={"username": "username", "password": self._auth_password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        response.raise_for_status()

        return str(response.json()["access_token"])

    @retry_with_login
    def pop_queue(
        self,
        task_capabilities: list[str],
        reachable_networks: list[str],
    ) -> LuikPopResponse | None:
        try:
            response = self.session.post(
                f"/pop/{self._queue}",
                json=LuikPopRequest(
                    task_capabilities=task_capabilities,
                    reachable_networks=reachable_networks,
                ).model_dump(),
            )

            logger.info(response, content=response.text)

            if response.status_code == 200:
                return LuikPopResponse.model_validate_json(response.content)
            elif response.status_code == 204:  # no content
                return None
            elif response.status_code == 401:
                response.raise_for_status()
            elif response.is_error:
                logger.error(
                    "Something went wrong with popping queue.",
                    queue=self._queue,
                    response=response.content,
                )
                return None
        except ConnectError as e:
            logger.error("Failed to connect to Luik.", error=str(e))

        return None
