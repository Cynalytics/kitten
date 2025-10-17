import structlog
from httpx import Client, ConnectError

from kitten.models.api_models import (
    BoefjeInputResponse,
    BoefjeOutput,
    LuikPopRequest,
    LuikPopResponse,
)

logger = structlog.get_logger(__name__)


class LuikClientInterface:
    def pop_queue(
        self, task_capabilities: list[str], reachable_networks: list[str]
    ) -> LuikPopResponse | None:
        raise NotImplementedError()

    def boefje_input(self, task_id: str) -> BoefjeInputResponse:
        raise NotImplementedError()

    def boefje_output(self, task_id: str, boefje_output: BoefjeOutput) -> None:
        raise NotImplementedError()


class LuikClient(LuikClientInterface):
    def __init__(self, base_url: str, auth_token: str):
        self.session = Client(
            base_url=base_url,
            headers={"luik-api-key": auth_token},
        )

    def pop_queue(
        self,
        task_capabilities: list[str],
        reachable_networks: list[str],
    ) -> LuikPopResponse | None:
        try:
            response = self.session.post(
                "/pop",
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
                    response=response.content,
                )
                return None
        except ConnectError as e:
            logger.error("Failed to connect to Luik.", error=str(e))

        return None

    def boefje_input(
        self, task_id: str
    ) -> BoefjeInputResponse:  # TODO: return object instead of raw  text
        response = self.session.get(f"/boefje/input/{task_id}")
        response.raise_for_status()
        logger.info("Boefje input sent", task_id=task_id, response=response.text)
        return BoefjeInputResponse.model_validate_json(response.content)

    def boefje_output(self, task_id: str, boefje_output: BoefjeOutput) -> None:
        response = self.session.post(
            f"/boefje/output/{task_id}", json=boefje_output.model_dump()
        )
        
        if response.is_error:
            logger.error(
                "Failed to send Boefje output",
                task_id=task_id,
                status=response.status_code,
                response=response.text,
            )
        response.raise_for_status()
        logger.info(
            "Boefje output sent",
            task_id=task_id,
            response=response.text,
            status=boefje_output.status,
        )
