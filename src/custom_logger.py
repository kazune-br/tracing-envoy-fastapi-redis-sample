import logging
import os
import sys

from loguru import logger

LOG_LEVEL = "INFO"
if os.getenv("ENV") == "dev":
    print("DEV")
    SERIALIZE = False
    BACKTRACE = True
    DIAGNOSE = True
    COLORIZE = True
else:
    print("Other")
    SERIALIZE = True
    BACKTRACE = False
    DIAGNOSE = False
    COLORIZE = False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "serialize": SERIALIZE,
                "backtrace": BACKTRACE,
                "diagnose": DIAGNOSE,
                "colorize": COLORIZE,
                "level": LOG_LEVEL,
            }
        ]
    )
