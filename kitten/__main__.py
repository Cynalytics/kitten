import json
import logging.config
import time

import docker
import httpx
import structlog

from kitten.config import settings
from kitten.models.api_models import LuikPopResponse

with settings.log_cfg.open() as f:
    logging.config.dictConfig(json.load(f))

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper("iso", utc=False),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
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
