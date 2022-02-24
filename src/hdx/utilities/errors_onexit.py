"""Collect and log errors on exit"""
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


class ErrorsOnExit:
    """Class that enables recording of errors with logging of those errors on exit"""

    def __init__(self) -> None:
        self.errors = list()

    def add(self, message: str) -> None:
        """Add error to be logged later

        Args:
            message (str): Error message

        Returns:
            None
        """
        self.errors.append(message)

    def log(self) -> None:
        """Log errors

        Returns:
            None
        """
        for error in self.errors:
            logger.error(error)

    def exit_on_error(self) -> None:
        """Exit with a 1 code if there are errors

        Returns:
            None
        """
        if self.errors:
            sys.exit(1)

    def log_exit_on_error(self) -> None:
        """Log errors and exit with a 1 code if there are errors

        Returns:
            None
        """
        self.log()
        self.exit_on_error()

    def __enter__(self) -> "ErrorsOnExit":
        logging.errors_on_exit = self
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.log_exit_on_error()
