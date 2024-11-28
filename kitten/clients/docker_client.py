import docker
import structlog

from kitten.models.docker_models import DockerRunResponse


logger = structlog.get_logger(__name__)


class NoOciImageException(Exception):
    def __init__(self, extra: str = ""):
        super().__init__(f"No oci_image has been given. {extra}")


class DockerClientInterface:
    def run_boefje(self, oci_image: str, input_url: str) -> DockerRunResponse:
        raise NotImplementedError()


class DockerClient(DockerClientInterface):
    def __init__(self):
        self._docker_client = docker.from_env()

    def run_boefje(self, oci_image: str, input_url: str) -> DockerRunResponse:
        container = self._docker_client.containers.run(
            image=oci_image,
            command=input_url,
            remove=True,
            network="host",
            detach=True,
        )

        if not (container.id and (container.image and container.image.id)):
            raise Exception("Ran container either doesn't have an id or an image")

        return DockerRunResponse(id=container.id, image=container.image.id)
