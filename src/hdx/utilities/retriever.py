import logging
from collections.abc import Iterator, Sequence
from copy import deepcopy
from os import mkdir
from os.path import join
from shutil import rmtree
from typing import Any

from slugify import slugify

from hdx.utilities.base_downloader import BaseDownload, DownloadError
from hdx.utilities.downloader import Download
from hdx.utilities.loader import load_json, load_text, load_yaml
from hdx.utilities.path import get_filename_extension_from_url
from hdx.utilities.saver import save_json, save_text, save_yaml

logger = logging.getLogger(__name__)


class Retrieve(BaseDownload):
    """Retrieve class which takes in a Download object and can either download,
    download and save or use previously downloaded and saved data. It also
    allows the use of a static fallback when downloading fails.

    Args:
        downloader: Download object
        fallback_dir: Directory containing static fallback data
        saved_dir: Directory to save or load downloaded data
        temp_dir: Temporary directory for when data is not needed after downloading
        save: Whether to save downloaded data. Defaults to False.
        use_saved: Whether to use saved data. Defaults to False.
        prefix: Prefix to add to filenames. Defaults to "".
        delete: Whether to delete saved_dir if save is True. Defaults to True.
        log_level: Level at which to log messages. Defaults to logging.INFO.
    """

    retrievers = {}

    def __init__(
        self,
        downloader: Download,
        fallback_dir: str,
        saved_dir: str,
        temp_dir: str,
        save: bool = False,
        use_saved: bool = False,
        prefix: str = "",
        delete: bool = True,
        log_level: int = logging.INFO,
    ):
        self.downloader = downloader
        self.fallback_dir = fallback_dir
        self.saved_dir = saved_dir
        self.temp_dir = temp_dir
        self.save = save
        self.use_saved = use_saved
        self.prefix = prefix
        self.check_flags(saved_dir, save, use_saved, delete)
        self.log_level = log_level

    @staticmethod
    def check_flags(saved_dir: str, save: bool, use_saved: bool, delete: bool) -> None:
        """Check flags. Also delete saved_dir if save and delete are True.

        Args:
            saved_dir: Directory to save or load downloaded data
            save: Whether to save downloaded data
            use_saved: Whether to use saved data
            delete: Whether to delete saved_dir if save is True

        Returns:
            None
        """
        if save:
            if use_saved:
                raise ValueError(
                    "Either the save or use_saved flags can be set to True!"
                )
            if delete:
                rmtree(saved_dir, ignore_errors=True)
                mkdir(saved_dir)

    @staticmethod
    def get_url_logstr(url: str) -> str:
        """Url string that will be logged. It is limited to 100 characters if
        necessary.

        Args:
            url: URL to download

        Returns:
            Url string to use in logs
        """
        if len(url) > 100:
            return f"{url[:100]}..."
        return url

    def clone(self, downloader: Download) -> "Retrieve":
        """Clone a given retriever but use the given downloader.

        Args:
            downloader: Downloader to use

        Returns:
            Cloned retriever
        """
        return Retrieve(
            downloader,
            fallback_dir=self.fallback_dir,
            saved_dir=self.saved_dir,
            temp_dir=self.temp_dir,
            save=self.save,
            use_saved=self.use_saved,
            prefix=self.prefix,
            delete=False,
        )

    def get_filename(
        self,
        url: str,
        filename: str | None = None,
        possible_extensions: tuple[str, ...] = tuple(),
        **kwargs: Any,
    ) -> tuple[str, Any]:
        """Get filename from url and given parameters.

        Args:
            url: Url from which to get filename
            filename: Filename to use. Defaults to None (infer from url).
            possible_extensions: Possible extensions to look for in url
            **kwargs: See below
            format (str): Given extension to look for in url
            file_type (str): Given extension to look for in url

        Returns:
            Tuple of (filename, kwargs)
        """
        prefix = kwargs.pop("file_prefix", self.prefix)
        if prefix:
            prefix = f"{prefix}_"
        if filename:
            return f"{prefix}{filename}", kwargs
        filename, extension = get_filename_extension_from_url(
            url, second_last=True, use_query=True
        )
        filename = slugify(filename)
        extensions = []
        format = kwargs.get("format")
        if format:
            extensions.append(format)
        file_type = kwargs.get("file_type")
        if file_type:
            extensions.append(file_type)
        if possible_extensions:
            extensions.extend(possible_extensions)
        if not extensions:
            return f"{prefix}{filename}{extension}", kwargs
        first_ext = f".{extensions[0].lower()}"
        if not extension:
            return f"{prefix}{filename}{first_ext}", kwargs
        for candidate in extensions:
            if candidate == extension[1:]:
                return f"{prefix}{filename}{extension}", kwargs
        filename = slugify(f"{filename}{extension}")
        return f"{prefix}{filename}{first_ext}", kwargs

    def set_bearer_token(self, bearer_token: str) -> None:
        """Set bearer token in downloader

        Args:
            bearer_token: Bearer token

        Returns:
            None
        """
        self.downloader.set_bearer_token(bearer_token)

    def download_file(
        self,
        url: str,
        filename: str | None = None,
        logstr: str | None = None,
        fallback: bool = False,
        log_level: int = None,
        **kwargs: Any,
    ) -> str:
        """Retrieve file.

        Args:
            url: URL to download
            filename: Filename of saved file. Defaults to getting from url.
            logstr: Text to use in log string to describe download. Defaults to filename.
            fallback: Whether to use static fallback if download fails. Defaults to False.
            log_level: Level at which to log messages. Overrides level from constructor.
            **kwargs: Parameters to pass to download_file call

        Returns:
            Path to downloaded file
        """
        if log_level is None:
            log_level = self.log_level
        filename, kwargs = self.get_filename(url, filename, **kwargs)
        if not logstr:
            logstr = filename
        if self.save:
            folder = self.saved_dir
        else:
            folder = self.temp_dir
        output_path = join(folder, filename)
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.log(log_level, f"Using saved {logstr} in {saved_path}")
            return saved_path
        try:
            logger.log(
                log_level,
                f"Downloading {logstr} from {self.get_url_logstr(url)} into {output_path}",
            )
            return self.downloader.download_file(url, path=output_path, **kwargs)
        except DownloadError:
            if not fallback:
                raise
            fallback_path = join(self.fallback_dir, filename)
            logger.exception(
                f"{logstr} download failed, using static data {fallback_path}!"
            )
            return fallback_path

    def download_text(
        self,
        url: str,
        filename: str | None = None,
        logstr: str | None = None,
        fallback: bool = False,
        log_level: int = None,
        **kwargs: Any,
    ) -> str:
        """Download text.

        Args:
            url: URL to download
            filename: Filename of saved file. Defaults to getting from url.
            logstr: Text to use in log string to describe download. Defaults to filename.
            fallback: Whether to use static fallback if download fails. Defaults to False.
            log_level: Level at which to log messages. Overrides level from constructor.
            **kwargs: Parameters to pass to download_text call

        Returns:
            The text from the file
        """
        if log_level is None:
            log_level = self.log_level
        filename, kwargs = self.get_filename(url, filename, **kwargs)
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.log(log_level, f"Using saved {logstr} in {saved_path}")
            text = load_text(saved_path)
        else:
            try:
                logger.log(
                    log_level,
                    f"Downloading {logstr} from {self.get_url_logstr(url)}",
                )
                text = self.downloader.download_text(url, **kwargs)
                if self.save:
                    logger.log(log_level, f"Saving {logstr} in {saved_path}")
                    save_text(text, saved_path)
            except DownloadError:
                if not fallback:
                    raise
                fallback_path = join(self.fallback_dir, filename)
                logger.exception(
                    f"{logstr} download failed, using static data {fallback_path}!"
                )
                text = load_text(fallback_path)
        return text

    def download_yaml(
        self,
        url: str,
        filename: str | None = None,
        logstr: str | None = None,
        fallback: bool = False,
        log_level: int = None,
        **kwargs: Any,
    ) -> Any:
        """Retrieve YAML.

        Args:
            url: URL to download
            filename: Filename of saved file. Defaults to getting from url.
            logstr: Text to use in log string to describe download. Defaults to filename.
            fallback: Whether to use static fallback if download fails. Defaults to False.
            log_level: Level at which to log messages. Overrides level from constructor.
            **kwargs: Parameters to pass to download_yaml call

        Returns:
            The data from the YAML file
        """
        if log_level is None:
            log_level = self.log_level
        filename, kwargs = self.get_filename(url, filename, ("yaml", "yml"), **kwargs)
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.log(log_level, f"Using saved {logstr} in {saved_path}")
            ryaml = load_yaml(saved_path)
        else:
            try:
                logger.log(
                    log_level,
                    f"Downloading {logstr} from {self.get_url_logstr(url)}",
                )
                ryaml = self.downloader.download_yaml(url, **kwargs)
                if self.save:
                    logger.log(log_level, f"Saving {logstr} in {saved_path}")
                    save_yaml(ryaml, saved_path)
            except DownloadError:
                if not fallback:
                    raise
                fallback_path = join(self.fallback_dir, filename)
                logger.exception(
                    f"{logstr} download failed, using static data {fallback_path}!"
                )
                ryaml = load_yaml(fallback_path)
        return ryaml

    def download_json(
        self,
        url: str,
        filename: str | None = None,
        logstr: str | None = None,
        fallback: bool = False,
        log_level: int = None,
        **kwargs: Any,
    ) -> Any:
        """Retrieve JSON.

        Args:
            url: URL to download
            filename: Filename of saved file. Defaults to getting from url.
            logstr: Text to use in log string to describe download. Defaults to filename.
            fallback: Whether to use static fallback if download fails. Defaults to False.
            log_level: Level at which to log messages. Overrides level from constructor.
            **kwargs: Parameters to pass to download_json call

        Returns:
            The data from the JSON file
        """
        if log_level is None:
            log_level = self.log_level
        filename, kwargs = self.get_filename(url, filename, ("json",), **kwargs)
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.log(log_level, f"Using saved {logstr} in {saved_path}")
            rjson = load_json(saved_path)
        else:
            try:
                logger.log(
                    log_level,
                    f"Downloading {logstr} from {self.get_url_logstr(url)}",
                )
                rjson = self.downloader.download_json(url, **kwargs)
                if self.save:
                    logger.log(log_level, f"Saving {logstr} in {saved_path}")
                    save_json(rjson, saved_path)
            except DownloadError:
                if not fallback:
                    raise
                fallback_path = join(self.fallback_dir, filename)
                logger.exception(
                    f"{logstr} download failed, using static data {fallback_path}!"
                )
                rjson = load_json(fallback_path)
        return rjson

    def get_tabular_rows(
        self,
        url: str | Sequence[str],
        has_hxl: bool = False,
        headers: int | Sequence[int] | Sequence[str] = 1,
        dict_form: bool = False,
        filename: str | None = None,
        logstr: str | None = None,
        fallback: bool = False,
        **kwargs: Any,
    ) -> tuple[list[str], Iterator[list | dict]]:
        """Returns header of tabular file(s) pointed to by url and an iterator
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
            has_hxl: Whether files have HXL hashtags. Defaults to False.
            headers: Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form: Return dict or list for each row. Defaults to False (list)
            filename: Filename of saved file. Defaults to getting from url.
            logstr: Text to use in log string to describe download. Defaults to filename.
            fallback: Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_file and get_tabular_rows calls

        Returns:
            Tuple (headers, iterator where each row is a list or dictionary)
        """
        if isinstance(url, list):
            is_list = True
            orig_kwargs = deepcopy(kwargs)
            urls = url
            url = urls[0]
        else:
            is_list = False
        path = self.download_file(url, filename, logstr, fallback, **kwargs)
        if is_list:
            path = [path]
            for url in urls[1:]:
                temp_kwargs = deepcopy(orig_kwargs)
                pth = self.download_file(url, None, logstr, fallback, **temp_kwargs)
                path.append(pth)

        kwargs.pop("file_prefix", None)
        return self.downloader.get_tabular_rows(
            path, has_hxl, headers, dict_form, **kwargs
        )

    @classmethod
    def generate_retrievers(
        cls,
        fallback_dir: str,
        saved_dir: str,
        temp_dir: str,
        save: bool = False,
        use_saved: bool = False,
        ignore: Sequence[str] = tuple(),
        delete: bool = True,
        **kwargs: Any,
    ) -> None:
        """Generate retrievers. Retrievers are generated from downloaders so
        Download.generate_downloaders() needs to have been called first. Each
        retriever can either download, download and save or use previously
        downloaded and saved data. It also allows the use of a static fallback
        when downloading fails.

        Args:
            fallback_dir: Directory containing static fallback data
            saved_dir: Directory to save or load downloaded data
            temp_dir: Temporary directory for when data is not needed after downloading
            save: Whether to save downloaded data. Defaults to False.
            use_saved: Whether to use saved data. Defaults to False.
            ignore: Don't generate retrievers for these downloaders
            delete: Whether to delete saved_dir if save is True. Defaults to True.
            **kwargs (Any): Any other arguments to pass.

        Returns:
            None
        """
        cls.check_flags(saved_dir, save, use_saved, delete)
        cls.retrievers = {}
        for name, downloader in Download.downloaders.items():
            if name in ignore:
                continue
            cls.retrievers[name] = cls(
                downloader,
                fallback_dir,
                saved_dir,
                temp_dir,
                save,
                use_saved,
                delete=False,
                **kwargs,
            )

    @classmethod
    def get_retriever(cls, name: str | None = None) -> "Retrieve":
        """Get a generated retriever given a name. If name is not supplied, the
        default one will be returned.

        Args:
            name: Name of retriever. Defaults to None (get default).

        Returns:
            Retriever object
        """
        return cls.retrievers.get(name, cls.retrievers["default"])
