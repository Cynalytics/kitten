import logging
import structlog

from kitten.app import get_kitten_docker_runner
import kitten.api
from kitten.config import settings


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
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.INFO
    ),  # TODO: make logging use env
    cache_logger_on_first_use=True,
)

logger = structlog.getLogger(__name__)


def main():
    logger.debug("Running kitten with settings", **settings.model_dump())

    kitten.api.run()

    runner = get_kitten_docker_runner(
        str(settings.luik_api),
        str(settings.kitten_api),
        settings.boefje_task_capabilities,
        settings.boefje_reachable_networks,
        settings.worker_heartbeat,
        settings.auth_password,
    )
    runner.run()
    logger.info("runner has quit. 👋")


if __name__ == "__main__":
    main()
