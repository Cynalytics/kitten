import structlog

from kitten.app import get_kitten_docker_runner
from kitten.config import settings
from kitten.logging import configure_logging


configure_logging()
logger = structlog.getLogger(__name__)


def main():
    logger.debug("Running kitten with settings", **settings.model_dump())

    runner = get_kitten_docker_runner(
        str(settings.luik_api),
        settings.boefje_task_capabilities,
        settings.boefje_reachable_networks,
        settings.worker_heartbeat,
        settings.luik_auth_token,
    )
    runner.run()
    logger.info("runner has quit. 👋")


if __name__ == "__main__":
    main()
