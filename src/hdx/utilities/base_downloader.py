from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from typing import Any


class DownloadError(Exception):
    pass


class BaseDownload(ABC):
    """Base download class with various download operations that subclasses
    should implement."""

    def __enter__(self) -> "BaseDownload":
        """Allow usage of with.

        Returns:
            Download object
        """
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Subclasses should define this to allow with usage.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            traceback: Traceback

        Returns:
            None
        """

    @abstractmethod
    def download_file(self, url: str, *args: Any, **kwargs: Any) -> str:
        """Download file from url.

        Args:
            url: URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            Path of downloaded file
        """

    @abstractmethod
    def download_text(self, url: str, *args: Any, **kwargs: Any) -> str:
        """Download text from url.

        Args:
            url: URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            The text from the file
        """

    @abstractmethod
    def download_yaml(self, url: str, *args: Any, **kwargs: Any) -> Any:
        """Download YAML from url.

        Args:
            url: URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            The data from the YAML file
        """

    @abstractmethod
    def download_json(self, url: str, *args: Any, **kwargs: Any) -> Any:
        """Download JSON from url.

        Args:
            url: URL or path to download
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            The data from the JSON file
        """

    @abstractmethod
    def get_tabular_rows(
        self,
        url: str | Sequence[str],
        has_hxl: bool = False,
        headers: int | Sequence[int] | Sequence[str] = 1,
        dict_form: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[list[str], Iterator[list | dict]]:
        """Returns header of tabular file pointed to by url and an iterator
        where each row is returned as a list or dictionary depending on the
        dict_rows argument.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1.
        The dict_form arguments specifies if each row should be returned as a dictionary
        or a list, defaulting to a list.

        Args:
            url: A single or list of URLs or paths to read from
            has_hxl: Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers: Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form: Return dict or list for each row. Defaults to False (list)
            *args (Any): Positional arguments
            **kwargs (Any): Keyword arguments

        Returns:
            Tuple (headers, iterator where each row is a list or dictionary)
        """
