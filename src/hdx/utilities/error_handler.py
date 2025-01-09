"""Collect errors and warnings by category and log them."""

import logging
import sys
from typing import Any

from hdx.utilities.dictandlist import dict_of_sets_add
from hdx.utilities.typehint import ListTuple

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Class that enables recording of errors and warnings. They can be logged
    by calling output_errors or automatically logged on exit and are output
    grouped by category and sorted."""

    def __init__(
        self,
    ):
        self.shared_errors = {
            "error": {},
            "warning": {},
        }

    def add_message(
        self, category: str, message: str, message_type: str = "error"
    ) -> None:
        """Add error to be logged.

        Args:
            category (str): Error category
            message (str): Error message
            message_type (str): The type of message (error or warning). Default is "error"

        Returns:
            None
        """
        dict_of_sets_add(self.shared_errors[message_type], category, message)

    def add_missing_value_message(
        self,
        category: str,
        value_type: str,
        value: str,
        message_type: str = "error",
    ) -> None:
        """
        Add a new message (typically a warning or error) concerning a missing value
        to a dictionary of messages in a fixed format:
            error category - {text}
        identifier is usually a dataset name.
        Args:
            category (str): Error category
            value_type (str): Type of value e.g. "sector"
            value (str): Missing value
            message_type (str): The type of message (error or warning). Default is "error"
        Returns:
            None
        """
        text = f"{value_type} {value} not found"
        self.add_message(category, text, message_type)

    def add_multi_valued_message(
        self,
        category: str,
        text: str,
        values: ListTuple,
        message_type: str = "error",
    ) -> bool:
        """
        Add a new message (typically a warning or error) concerning a list of
        values to a set of messages in a fixed format:
            error category - n {text}. First 10 values: n1,n2,n3...
        If less than 10 values, ". First 10 values" is omitted. identifier is usually
        a dataset name. Values are cast to string.

        Args:
            category (str): Error category
            text (str): Text to use e.g. "negative values removed"
            values (ListTuple): List of values of concern
            message_type (str): The type of message (error or warning). Default is "error"
        Returns:
            bool: True if a message was added, False if not
        """
        if not values:
            return False
        no_values = len(values)
        if no_values > 10:
            values = values[:10]
            msg = ". First 10 values"
        else:
            msg = ""
        text = f"{no_values} {text}{msg}: {', '.join(map(str, values))}"
        self.add_message(category, text, message_type)
        return True

    def output_errors(self) -> None:
        """
        Log errors by category

        Returns:
            None
        """

        for _, errors in self.shared_errors["error"].items():
            errors = sorted(errors)
            for error in errors:
                logger.error(error)
        for _, warnings in self.shared_errors["warning"].items():
            warnings = sorted(warnings)
            for warning in warnings:
                logger.warning(warning)

    def exit_on_error(self) -> None:
        """Exit with a 1 code if there are errors.

        Returns:
            None
        """
        if self.shared_errors["error"]:
            sys.exit(1)

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.output_errors()
        if exc_type is None:
            self.exit_on_error()
