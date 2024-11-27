import structlog
import time

import docker

from kitten.clients.luik_client import LuikClient
from kitten.config import settings


class KittenRunner:
    def run(self) -> None:
        raise NotImplementedError()


class KittenDockerRunner(KittenRunner):
    def __init__(self) -> None:
        self.logger = structlog.get_logger(KittenDockerRunner.__name__)
        self.luik_client = LuikClient(str(settings.luik_api))
        self.docker_client = docker.from_env()

    def run(self) -> None:
        while True:
            self.logger.info("Waiting for %s seconds.", settings.worker_heartbeat)
            time.sleep(settings.worker_heartbeat)

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
