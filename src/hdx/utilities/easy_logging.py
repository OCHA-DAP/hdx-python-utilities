"""Configuration of logging"""
import logging
from sys import stdout

from loguru import logger


def setup_logging(error_file: bool = False) -> None:
    """Setup logging configuration. intercepts standard logging and outputs errors to
    a file.

    Args:
        error_file (bool): Whether to output errors.log file. Defaults to False.

    Returns:
        None
    """
    logger.add(stdout, colorize=True, backtrace=True, diagnose=True)

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(
                colors=True,
                record=True,
                depth=depth,
                exception=record.exc_info,
            ).log(level, record.getMessage())

    if error_file:
        logger.add(
            "errors.log",
            level="ERROR",
            mode="w",
            backtrace=True,
            diagnose=True,
        )
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET)
