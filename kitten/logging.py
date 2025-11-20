import structlog

# from kitten.config import settings
# TODO
# with settings.log_cfg.open() as f:
#     logging.config.dictConfig(json.load(f))


def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper("iso", utc=False),
            (
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    pad_level=False,
                    exception_formatter=structlog.dev.plain_traceback,
                )
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
