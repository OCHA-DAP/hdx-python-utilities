"""Utility to save state to a file and read it back."""

import logging
from typing import Any, Callable, Dict

from hdx.utilities.dateparse import iso_string_from_datetime, parse_date
from hdx.utilities.loader import load_text
from hdx.utilities.saver import save_text

logger = logging.getLogger(__name__)


class State:
    """State class that allows the reading and writing of state to a given
    path. Input and output state transformations can be supplied in read_fn and
    write_fn respectively. The input state transformation takes in a string
    while the output transformation outputs a string. If run inside a GitHub
    Action, the saved state file could be committed to GitHub so that on next
    run the state is available in the repository.

    Args:
        path (str): Path to save state file
        read_fn (Callable[[str], Any]): Input state transformation. Defaults to lambda x: x.
        write_fn: Callable[[Any], str]: Output state transformation. Defaults to lambda x: x.
    """

    def __init__(
        self,
        path: str,
        read_fn: Callable[[str], Any] = lambda x: x,
        write_fn: Callable[[Any], str] = lambda x: x,
    ) -> None:
        self.path = path
        self.read_fn = read_fn
        self.write_fn = write_fn
        self.state = self.read()

    def __enter__(self) -> "State":
        """Allow usage of with.

        Returns:
            State: SavedState object
        """
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Allow usage of with.

        Args:
            exc_type (Any): Exception type
            exc_value (Any): Exception value
            traceback (Any): Traceback

        Returns:
            None
        """
        self.write()

    def read(self) -> Any:
        """Read state from file

        Returns:
            Any: State
        """
        value = self.read_fn(load_text(self.path))
        logger.info(f"State read from {self.path} = {value}")
        return value

    def write(self) -> None:
        """Write state to file

        Returns:
            None
        """
        logger.info(f"State written to {self.path} = {self.state}")
        save_text(self.write_fn(self.state), self.path)

    def get(self) -> Any:
        """Get the state

        Returns:
            Any: State
        """
        return self.state

    def set(self, state: Any):
        """Set the state

        Args:
            state (Any): State

        Returns:
            None
        """
        self.state = state

    @staticmethod
    def dates_str_to_country_date_dict(dates_str: str) -> Dict:
        """Convert a comma separated string of key=date string pairs eg.
        "default=2017-01-01,afg=2019-01-01" to a dictionary of key date
        mappings eg.
        {"default": 2017-01-01 as datetime, "afg": 2019-01-01 as datetime}

        Args:
            dates_str (str): Comma separated string of key=date string pairs

        Returns:
            Dict: Dictionary of key date mappings
        """
        result = {}
        for keyvalue in dates_str.split(","):
            key, value = keyvalue.split("=")
            result[key] = parse_date(value)
        return result

    @staticmethod
    def country_date_dict_to_dates_str(country_date_dict: Dict) -> str:
        """Convert a dictionary of key date mappings eg.
        {"default": 2017-01-01 as datetime, "afg": 2019-01-01 as datetime}
        to a comma separated string of key=date string pairs eg.
        "default=2017-01-01,afg=2019-01-01"

        Args:
            country_date_dict (Dict): Dictionary of key date mappings

        Returns:
            str: Comma separated string of key=date string pairs
        """
        strlist = []
        for key, value in country_date_dict.items():
            valstr = iso_string_from_datetime(value)
            strlist.append(f"{key}={valstr}")
        return ",".join(strlist)
