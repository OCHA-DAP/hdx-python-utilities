from abc import ABC, abstractmethod
from typing import Any, Iterator, List, Tuple, Union

from hdx.utilities.typehint import ListDict, ListTuple


class DownloadError(Exception):
    pass


class BaseDownload(ABC):
    """Base download class with various download operations that subclasses should
    implement.
    """

    def __enter__(self) -> "BaseDownload":
        """
        Allow usage of with

        Returns:
            BaseDownload: Download object

        """
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """
        Subclasses should define this to allow with usage

        Args:
            exc_type (Any): Exception type
            exc_value (Any): Exception value
            traceback (Any): Traceback

        Returns:
            None

        """
        pass

    @abstractmethod
    def download_file(self, url: str, *args: Any, **kwargs: Any) -> str:
        """Download file from url

        Args:
            url (str): URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            str: Path of downloaded file

        """

    @abstractmethod
    def download_text(self, url: str, *args: Any, **kwargs: Any) -> str:
        """Download text from url

        Args:
            url (str): URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            str: The text from the file

        """

    @abstractmethod
    def download_yaml(self, url: str, *args: Any, **kwargs: Any) -> Any:
        """Download YAML from url

        Args:
            url (str): URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            Any: The data from the YAML file

        """

    @abstractmethod
    def download_json(self, url: str, *args: Any, **kwargs: Any) -> Any:
        """Download JSON from url

        Args:
            url (str): URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            Any: The data from the JSON file

        """

    @abstractmethod
    def get_tabular_rows(
        self,
        url: str,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        dict_form: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[List[str], Iterator[ListDict]]:
        """Returns header of tabular file pointed to by url and an iterator where each
        row is returned as a list or dictionary depending on the dict_rows argument.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1.
        The dict_form arguments specifies if each row should be returned as a dictionary
        or a list, defaulting to a list.

        Args:
            url (str): URL or path to read from
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form (bool): Return dict or list for each row. Defaults to False (list)
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            Tuple[List[str],Iterator[ListDict]]: Tuple (headers, iterator where each row is a list or dictionary)

        """
