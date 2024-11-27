import structlog
import time
import signal


from kitten.clients.docker_client import DockerClient
from kitten.clients.luik_client import LuikClient


class KittenRunner:
    def run(self) -> None:
        raise NotImplementedError()

    def _exit(self) -> None:
        raise NotImplementedError()


class KittenDockerRunner(KittenRunner):
    def __init__(
        self,
        luik_api: str,
        queue: str,
        runner_task_capabilities: list[str],
        runner_reachable_networks: list[str],
        runner_heartbeat: int,
    ):
        self.logger = structlog.get_logger(KittenDockerRunner.__name__)
        self.luik_client = LuikClient(luik_api, queue)
        self.docker_client = DockerClient()

        self.runner_task_capabilities = runner_task_capabilities
        self.runner_reachable_networks = runner_reachable_networks

        self.runner_heartbeat = runner_heartbeat

        self.active = True

    def run(self) -> None:
        signal.signal(signal.SIGINT, lambda signum, _: self._exit(signum))
        signal.signal(signal.SIGTERM, lambda signum, _: self._exit(signum))

        while self.active:
            self.logger.info("Popping task")
            luik_pop_response = self.luik_client.pop_queue(
                self.runner_task_capabilities,
                self.runner_reachable_networks,
            )
            if luik_pop_response:
                self.logger.info(
                    "Going to run %s for task %s",
                    luik_pop_response.oci_image,
                    luik_pop_response.task_id,
                )
                container = self.docker_client.run_boefje(
                    luik_pop_response.oci_image,
                    str(self.luik_client.session.base_url).rstrip("/")
                    + f"/boefje/input/{luik_pop_response.task_id}",
                )

                self.logger.info("Container %s is running", container.id)

            self.logger.info("Waiting for %s seconds.", self.runner_heartbeat)
            time.sleep(self.runner_heartbeat)

    def _exit(self, signum: int | None = None):
        if signum:
            self.logger.info("Received %s, exiting", signal.Signals(signum).name)
        else:
            self.logger.info("Exiting without signum")

        self.active = False
