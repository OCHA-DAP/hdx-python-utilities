"""Logging Tests"""
import logging

from loguru import logger

from hdx.utilities.easy_logging import setup_logging

setup_logging(log_file="errors.log")


standard_logger = logging.getLogger(__name__)


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
            except ZeroDivisionError:
                standard_logger.exception(text)

            assert text in caplog.text

            text = "Another zero error!"
            try:
                divide(2, 0)
            except ZeroDivisionError:
                logger.exception(text)

            assert text in caplog.text
