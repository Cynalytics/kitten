import structlog
from httpx import Client, HTTPTransport, ConnectError

from kitten.models.api_models import LuikPopResponse

logger = structlog.get_logger(__name__)


class LuikClient:
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=3))

    def pop_queue(
        self,
        queue: str,
        boefje_task_capabilities: list[str],
        boefje_reachable_networks: list[str],
    ):
        try:
            response = self._session.post(
                f"/pop/{queue}",
                json={
                    "task_capabilities": boefje_task_capabilities,
                    "reachable_networks": boefje_reachable_networks,
                },
            )

            logger.info(response, content=response.text)

            if response.status_code == 200:
                return LuikPopResponse.model_validate_json(response.content)
            elif response.status_code == 204:  # no content
                return None
            elif response.is_error:
                logger.error(
                    "Something went wrong with popping queue.",
                    queue=queue,
                    response=response.content,
                )
                return None
        except ConnectError as e:
            logger.error("Failed to connect to Luik.", error=str(e))
            return None
