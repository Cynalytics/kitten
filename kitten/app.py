import structlog
import time
import signal

import docker

from kitten.clients.luik_client import LuikClient
from kitten.config import settings


class KittenRunner:
    def run(self) -> None:
        raise NotImplementedError()

    def exit(self) -> None:
        raise NotImplementedError()


class KittenDockerRunner(KittenRunner):
    def __init__(self) -> None:
        self.logger = structlog.get_logger(KittenDockerRunner.__name__)
        self.luik_client = LuikClient(str(settings.luik_api))
        self.docker_client = docker.from_env()

        self.active = True

    def run(self) -> None:
        signal.signal(signal.SIGINT, lambda signum, _: self.exit(signum))
        signal.signal(signal.SIGTERM, lambda signum, _: self.exit(signum))

        while self.active:
            self.logger.info("Popping task")
            luik_pop_response = self.luik_client.pop_queue(
                settings.queue,
                settings.boefje_task_capabilities,
                settings.boefje_reachable_networks,
            )
            if luik_pop_response:
                self.logger.info(
                    "Going to run %s for task %s",
                    luik_pop_response.oci_image,
                    luik_pop_response.task_id,
                )
                container = self.docker_client.containers.run(
                    image=luik_pop_response.oci_image,
                    command=str(settings.luik_api).rstrip("/")
                    + f"/boefje/input/{luik_pop_response.task_id}",
                    remove=True,
                    network="host",
                    detach=True,
                )

                self.logger.info("Container %s is running", container.id)

            self.logger.info("Waiting for %s seconds.", settings.worker_heartbeat)
            time.sleep(settings.worker_heartbeat)

    def exit(self, signum: int | None = None):
        if signum:
            self.logger.info("Received %s, exiting", signal.Signals(signum).name)
        else:
            self.logger.info("Exiting without signum")

        self.active = False
