"""Configuration of logging"""
import logging

from loguru import logger


def setup_logging(error_file: bool = False) -> None:
    """Setup logging configuration. intercepts standard logging and outputs errors to
    a file.

    Args:
        error_file (bool): Whether to output errors.log file. Defaults to False.

    Returns:
        None
    """

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

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    if error_file:
        logger.add(
            "errors.log",
            level="ERROR",
            mode="w",
            backtrace=True,
            diagnose=True,
        )
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET)


try:
    import pytest
    from _pytest.logging import LogCaptureFixture

    @pytest.fixture
    def caplog(caplog: LogCaptureFixture) -> None:
        """Emitting logs from loguru's logger.log means that they will not show up in caplog
         which only works with Python standard logging. This adds the same `
         LogCaptureHandler` being used by caplog to hook into loguru.

        Args:
            caplog (LogCaptureFixture): caplog fixture

        Returns:
            None
        """

        class PropogateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        handler_id = logger.add(
            PropogateHandler(), format="{message} {extra}", level="TRACE"
        )
        yield caplog
        logger.remove(handler_id)

except ModuleNotFoundError:
    pass
