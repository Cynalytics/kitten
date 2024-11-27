import structlog


from kitten.app import KittenDockerRunner
from kitten.config import settings


def main():
    logger = structlog.getLogger(__name__)

    logger.debug("Running kitten with settings", **settings.model_dump())
    runner = KittenDockerRunner()
    runner.run()


if __name__ == "__main__":
    main()
