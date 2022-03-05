"""Configuration of logging"""
import logging
from sys import stderr
from typing import Optional

from loguru import logger


def setup_logging(
    console_log_level: str = "INFO",
    log_file: Optional[str] = None,
    file_log_level: str = "ERROR",
) -> None:
    """Setup logging configuration. intercepts standard logging and outputs errors to
    a file.

    Args:
        console_log_level (str): Log level to use for console output. Defaults to INFO.
        log_file (Optional[str]): Path of log file. Defaults to None (No log file).
        file_log_level (str): Log level to use for console output. Defaults to ERROR.

    Returns:
        None
    """
    logger.remove()
    logger.add(
        stderr,
        level=console_log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    if log_file:
        logger.add(
            log_file,
            level=file_log_level,
            mode="w",
            backtrace=True,
            diagnose=True,
        )

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
                depth=depth,
                exception=record.exc_info,
            ).log(level, record.getMessage())

    logging.basicConfig(
        handlers=[InterceptHandler()], level=logging.NOTSET, force=True
    )
