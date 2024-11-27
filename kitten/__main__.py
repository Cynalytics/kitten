import structlog

from kitten.app import KittenDockerRunner
from kitten.config import settings


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper("iso", utc=False),
        structlog.dev.ConsoleRenderer(colors=True, pad_level=False),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


logger = structlog.getLogger(__name__)


def main():
    logger.debug("Running kitten with settings", **settings.model_dump())
    runner = KittenDockerRunner()
    runner.run()
    logger.info("runner has quit. 👋")


if __name__ == "__main__":
    main()
