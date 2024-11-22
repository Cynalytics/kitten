import logging
import time

import docker
import httpx

from kitten.config import settings
from kitten.models.api_models import LuikPopResponse


logger = logging.getLogger(__name__)

client = httpx.Client(base_url=str(settings.luik_api))
docker_client = docker.from_env()

while True:
    logger.info("Sleeping...")
    time.sleep(settings.worker_heartbeat)

    logger.info("Popping task")
    response = client.post(
        f"/pop/{settings.queue}",
        json={
            "task_capabilities": settings.boefje_task_capabilities,
            "reachable_networks": settings.boefje_reachable_networks,
        },
    )
    logger.info(response)
    logger.info(response.content)
    response.raise_for_status()
    if response.content:
        pop_response = LuikPopResponse.model_validate_json(response.content)

        task_id = pop_response.task_id

        docker_client.containers.run(
            image=pop_response.oci_image,
            command=str(settings.luik_api).rstrip("/") + f"/boefje/input/{task_id}",
            remove=True,
            network="host",
            detach=True,
        )
