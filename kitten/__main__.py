import structlog
import time

import docker

from kitten.clients.luik_client import LuikClient
from kitten.config import settings

logger = structlog.getLogger(__name__)

luik_client = LuikClient(str(settings.luik_api))

docker_client = docker.from_env()

logger.debug("Running kitten", **settings.model_dump())

while True:
    logger.info("Waiting for %s seconds.", settings.worker_heartbeat)
    time.sleep(settings.worker_heartbeat)

    logger.info("Popping task")
    luik_pop_response = luik_client.pop_queue(
        settings.queue,
        settings.boefje_task_capabilities,
        settings.boefje_reachable_networks,
    )
    if luik_pop_response:
        logger.info(
            "Going to run %s for task %s",
            luik_pop_response.oci_image,
            luik_pop_response.task_id,
        )
        container = docker_client.containers.run(
            image=luik_pop_response.oci_image,
            command=str(settings.luik_api).rstrip("/")
            + f"/boefje/input/{luik_pop_response.task_id}",
            remove=True,
            network="host",
            detach=True,
        )

        logger.info("Container %s is running", container.id)
