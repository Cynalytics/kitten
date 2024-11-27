import docker
import structlog

from kitten.models.docker_models import DockerRunResponse


logger = structlog.get_logger(__name__)


class DockerClientInterface:
    def start_docker(
        self, task_capabilities: list[str], reachable_networks: list[str]
    ) -> DockerRunResponse | None:
        raise NotImplementedError()


class DockerClient(DockerClientInterface):
    def __init__(self):
        self._docker_client = docker.from_env()

    def run_boefje(
        self,
        oci_image: str,
        input_url: str,
    ) -> DockerRunResponse:
        container = self._docker_client.containers.run(
            image=oci_image,
            command=input_url,
            remove=True,
            network="host",
            detach=True,
        )
        return DockerRunResponse(id=container.id, image=container.image)
