import logging
from os import mkdir
from os.path import join
from shutil import rmtree
from typing import Any, Iterator, List, Optional, Tuple, Union

from slugify import slugify

from hdx.utilities.base_downloader import BaseDownload, DownloadError
from hdx.utilities.downloader import Download
from hdx.utilities.loader import load_json, load_text, load_yaml
from hdx.utilities.path import get_filename_extension_from_url
from hdx.utilities.saver import save_json, save_text, save_yaml
from hdx.utilities.typehint import ListDict, ListTuple

logger = logging.getLogger(__name__)


class Retrieve(BaseDownload):
    """Retrieve class which takes in a Download object and can either download, download
    and save or use previously downloaded and saved data. It also allows the use of a
    static fallback when downloading fails.

    Args:
        downloader (Download): Download object
        fallback_dir (str): Directory containing static fallback data
        saved_dir (str): Directory to save or load downloaded data
        temp_dir (str): Temporary directory for when data is not needed after downloading
        save (bool): Whether to save downloaded data. Defaults to False.
        use_saved (bool): Whether to use saved data. Defaults to False.
        prefix (str): Prefix to add to filenames. Defaults to "".
        delete (bool): Whether to delete saved_dir if save is True. Defaults to True.
    """

    retrievers = dict()

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
    ):
        self.downloader = downloader
        self.fallback_dir = fallback_dir
        self.saved_dir = saved_dir
        self.temp_dir = temp_dir
        self.save = save
        self.use_saved = use_saved
        self.prefix = prefix
        self.check_flags(saved_dir, save, use_saved, delete)

    @staticmethod
    def check_flags(
        saved_dir: str, save: bool, use_saved: bool, delete: bool
    ) -> None:
        """Check flags. Also delete saved_dir if save and delete are True

        Args:
            saved_dir (str): Directory to save or load downloaded data
            save (bool): Whether to save downloaded data
            use_saved (bool): Whether to use saved data
            delete (bool): Whether to delete saved_dir if save is True

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
        """Url string that will be logged. It is limited to 100 characters if necessary.

        Args:
            url (str): URL to download

        Returns:
            str: Url string to use in logs

        """
        if len(url) > 100:
            return f"{url[:100]}..."
        return url

    @classmethod
    def clone(cls, retriever: "Retrieve", downloader: Download):
        """Clone a given retriever but use teh given downloader

        Args:
            retriever (Retrieve): Retriever to clone
            downloader (Download): Downloader to use

        Returns:
            Retrieve: Cloned retriever

        """
        return cls(
            downloader,
            fallback_dir=retriever.fallback_dir,
            saved_dir=retriever.saved_dir,
            temp_dir=retriever.temp_dir,
            save=retriever.save,
            use_saved=retriever.use_saved,
            prefix=retriever.prefix,
            delete=False,
        )

    def get_filename(
        self,
        url: str,
        filename: Optional[str] = None,
        possible_extensions: Tuple[str, ...] = tuple(),
        **kwargs: Any,
    ) -> Tuple[str, Any]:
        """Get filename from url and given parameters

        Args:
            url (str): Url from which to get filename
            filename (optional[str]): Filename to use. Defaults to None (infer from url).
            possible_extensions (Tuple[str, ...]): Possible extensions to look for in url
            **kwargs: See below
            format (str): Given extension to look for in url
            file_type (str): Given extension to look for in url

        Returns:
            Retrieve: Cloned retriever

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
        extensions = list()
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

    def download_file(
        self,
        url: str,
        filename: Optional[str] = None,
        logstr: Optional[str] = None,
        fallback: bool = False,
        **kwargs: Any,
    ) -> str:
        """Retrieve file

        Args:
            url (str): URL to download
            filename (Optional[str]): Filename of saved file. Defaults to getting from url.
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_file call

        Returns:
            str: Path to downloaded file

        """
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
            logger.info(f"Using saved {logstr} in {saved_path}")
            return saved_path
        else:
            try:
                logger.info(
                    f"Downloading {logstr} from {self.get_url_logstr(url)} into {output_path}"
                )
                return self.downloader.download_file(
                    url, path=output_path, **kwargs
                )
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
        filename: Optional[str] = None,
        logstr: Optional[str] = None,
        fallback: bool = False,
        **kwargs: Any,
    ) -> str:
        """Download text

        Args:
            url (str): URL to download
            filename (Optional[str]): Filename of saved file. Defaults to getting from url.
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_text call

        Returns:
            str: The text from the file

        """
        filename, kwargs = self.get_filename(url, filename, **kwargs)
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.info(f"Using saved {logstr} in {saved_path}")
            text = load_text(saved_path)
        else:
            try:
                logger.info(
                    f"Downloading {logstr} from {self.get_url_logstr(url)}"
                )
                text = self.downloader.download_text(url, **kwargs)
                if self.save:
                    logger.info(f"Saving {logstr} in {saved_path}")
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
        filename: Optional[str] = None,
        logstr: Optional[str] = None,
        fallback: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Retrieve YAML

        Args:
            url (str): URL to download
            filename (Optional[str]): Filename of saved file. Defaults to getting from url.
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_yaml call

        Returns:
            Any: The data from the YAML file

        """
        filename, kwargs = self.get_filename(
            url, filename, ("yaml", "yml"), **kwargs
        )
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.info(f"Using saved {logstr} in {saved_path}")
            ryaml = load_yaml(saved_path)
        else:
            try:
                logger.info(
                    f"Downloading {logstr} from {self.get_url_logstr(url)}"
                )
                ryaml = self.downloader.download_yaml(url, **kwargs)
                if self.save:
                    logger.info(f"Saving {logstr} in {saved_path}")
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
        filename: Optional[str] = None,
        logstr: Optional[str] = None,
        fallback: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Retrieve JSON

        Args:
            url (str): URL to download
            filename (Optional[str]): Filename of saved file. Defaults to getting from url.
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_json call

        Returns:
            Any: The data from the JSON file

        """
        filename, kwargs = self.get_filename(
            url, filename, ("json",), **kwargs
        )
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.info(f"Using saved {logstr} in {saved_path}")
            rjson = load_json(saved_path)
        else:
            try:
                logger.info(
                    f"Downloading {logstr} from {self.get_url_logstr(url)}"
                )
                rjson = self.downloader.download_json(url, **kwargs)
                if self.save:
                    logger.info(f"Saving {logstr} in {saved_path}")
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
        url: str,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        dict_form: bool = False,
        filename: Optional[str] = None,
        logstr: Optional[str] = None,
        fallback: bool = False,
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
            filename (Optional[str]): Filename of saved file. Defaults to getting from url.
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_file call

        Returns:
            Tuple[List[str],Iterator[ListDict]]: Tuple (headers, iterator where each row is a list or dictionary)

        """
        path = self.download_file(url, filename, logstr, fallback, **kwargs)
        kwargs.pop("file_prefix", None)
        return self.downloader.get_tabular_rows(
            path, headers, dict_form, **kwargs
        )

    @classmethod
    def generate_retrievers(
        cls,
        fallback_dir: str,
        saved_dir: str,
        temp_dir: str,
        save: bool = False,
        use_saved: bool = False,
        ignore: ListTuple[str] = tuple(),
        delete: bool = True,
        **kwargs: Any,
    ) -> None:
        """Generate retrievers. Retrievers are generated from downloaders so
        Download.generate_downloaders() needs to have been called first. Each retriever
        can either download, download and save or use previously downloaded and saved
        data. It also allows the use of a static fallback when downloading fails.

        Args:
            fallback_dir (str): Directory containing static fallback data
            saved_dir (str): Directory to save or load downloaded data
            temp_dir (str): Temporary directory for when data is not needed after downloading
            save (bool): Whether to save downloaded data. Defaults to False.
            use_saved (bool): Whether to use saved data. Defaults to False.
            ignore (ListTuple[str]): Don't generate retrievers for these downloaders
            delete (bool): Whether to delete saved_dir if save is True. Defaults to True.
            **kwargs (Any): Any other arguments to pass.

        Returns:
            None
        """
        cls.check_flags(saved_dir, save, use_saved, delete)
        cls.retrievers = dict()
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
    def get_retriever(cls, name: Optional[str] = None) -> "Retrieve":
        """Get a generated retriever given a name. If name is not supplied, the default
        one will be returned.

        Args:
            name (Optional[str]): Name of retriever. Defaults to None (get default).

        Returns:
            Retriever: Retriever object
        """
        return cls.retrievers.get(name, cls.retrievers["default"])
