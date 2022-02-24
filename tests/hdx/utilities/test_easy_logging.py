"""Logging Tests"""
import logging

from loguru import logger

standard_logger = logging.getLogger(__name__)

from hdx.utilities.easy_logging import setup_logging

setup_logging(error_file=True)


class TestLogging:
    def test_setup_logging(self, caplog):
        with caplog.at_level(logging.ERROR):
            text = "This is an error!"
            standard_logger.error(text)
            assert text in caplog.text

            text = "Division by zero!"

            def divide(a, b):
                return a / b

            try:
                divide(1, 0)
            except:
                standard_logger.exception(text)

            assert text in caplog.text

            text = "Another zero error!"
            try:
                divide(2, 0)
            except:
                logger.exception(text)

            assert text in caplog.text
