from kitten.clients.docker_client import DockerClientInterface, NoOciImageException
from kitten.models.docker_models import DockerRunResponse


class MockDockerClient(DockerClientInterface):
    def run_boefje(self, oci_image: str, input_url: str) -> DockerRunResponse:
        if not oci_image:
            raise NoOciImageException(input_url)

        return DockerRunResponse(
            id="719c5bcbdbd20ab0e768418ec5a78040fd90c2e636dab8cfba17c27587aa162e",
            image=oci_image,
        )
