"""Collect errors and warnings by category and log them."""

import logging
import sys
from typing import Any, Optional

from hdx.utilities.dictandlist import dict_of_sets_add
from hdx.utilities.typehint import ListTuple

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Class that enables recording of errors and warnings.

    Errors and warnings can be logged by calling the `output` method or
    automatically logged on exit. Messages are output grouped by category and
    sorted.

    Args:
        should_exit_on_error (bool): Whether to exit with a 1 code if there are errors. Default is False.

    """

    def __init__(
        self,
        should_exit_on_error: bool = False,
    ):
        self.should_exit_on_error = should_exit_on_error
        self.shared_errors = {
            "error": {},
            "warning": {},
        }

    def add(
        self, message: str, category: str = "", message_type: str = "error"
    ) -> None:
        """Add error to be logged. Prepend category if supplied. Output format:
        error category - {text}

        Args:
            message (str): Error message
            category (str): Error category. Defaults to "".
            message_type (str): The type of message (error or warning). Default is "error"

        Returns:
            None
        """
        message = message.strip()
        if category:
            output = f"{category} - {message}"
        else:
            output = message
        dict_of_sets_add(self.shared_errors[message_type], category, output)

    @staticmethod
    def missing_value_message(value_type: str, value: Any) -> str:
        """
        Generate a formatted message for a missing value of a specific type in
        a fixed format:
            error category - type n not found

        Args:
            value_type (str): The type of value that is missing
            value (Any): The specific missing value

        Returns:
            str: A formatted message stating the missing value and its type
        """
        return f"{value_type} {str(value)} not found"

    def add_missing_value(
        self,
        value_type: str,
        value: Any,
        category: str = "",
        message_type: str = "error",
    ) -> None:
        """
        Add a new message (typically a warning or error) concerning a missing value
        to a dictionary of messages in a fixed format:
            error category - type n not found
        identifier is usually a dataset name.
        Args:
            value_type (str): Type of value e.g. "sector"
            value (Any): Missing value
            category (str): Error category. Defaults to "".
            message_type (str): The type of message (error or warning). Default is "error"
        Returns:
            None
        """
        self.add(
            self.missing_value_message(value_type, value),
            category,
            message_type,
        )

    def multi_valued_message(self, text: str, values: ListTuple) -> Optional[str]:
        """
        Generate a formatted message for a list of values in a fixed format:
            error category - n {text}. First 10 values: n1,n2,n3...
        If less than 10 values, ". First 10 values" is omitted. identifier is usually
        a dataset name. Values are cast to string.

        Args:
            text (str): Descriptive text for the issue (e.g., "invalid values")
            values (ListTuple): The list of related values of concern

        Returns:
            Optional[str]: A formatted string in the format defined above
        """
        if not values:
            return None
        no_values = len(values)
        if no_values > 10:
            values = values[:10]
            message_suffix = ". First 10 values"
        else:
            message_suffix = ""
        return f"{no_values} {text}{message_suffix}: {', '.join(map(str, values))}"

    def add_multi_valued(
        self,
        text: str,
        values: ListTuple,
        category: str = "",
        message_type: str = "error",
    ) -> bool:
        """
        Add a new message (typically a warning or error) concerning a list of
        values to a set of messages in a fixed format:
            error category - n {text}. First 10 values: n1,n2,n3...
        If less than 10 values, ". First 10 values" is omitted. identifier is usually
        a dataset name. Values are cast to string.

        Args:
            text (str): Text to use e.g. "negative values removed"
            values (ListTuple): List of values of concern
            category (str): Error category. Defaults to "".
            message_type (str): The type of message (error or warning). Default is "error"
        Returns:
            bool: True if a message was added, False if not
        """
        message = self.multi_valued_message(text, values)
        if message is None:
            return False
        self.add(message, category, message_type)
        return True

    def log(self) -> None:
        """
        Log warnings and errors by category and sorted

        Returns:
            None
        """

        for _, warnings in self.shared_errors["warning"].items():
            warnings = sorted(warnings)
            for warning in warnings:
                logger.warning(warning)
        for _, errors in self.shared_errors["error"].items():
            errors = sorted(errors)
            for error in errors:
                logger.error(error)

    def exit_on_error(self) -> None:
        """Exit with a 1 code if there are errors and should_exit_on_error
        is True

        Returns:
            None
        """
        if self.should_exit_on_error and self.shared_errors["error"]:
            sys.exit(1)

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.log()
        if exc_type is None:
            self.exit_on_error()
