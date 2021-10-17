import logging
from os import mkdir
from os.path import join
from shutil import rmtree

from hdx.utilities.downloader import DownloadError
from hdx.utilities.loader import load_file_to_str, load_json, load_yaml
from hdx.utilities.saver import save_json, save_str_to_file, save_yaml

logger = logging.getLogger(__name__)


class Retrieve:
    """Retrieve class which takes in a Download object and can either download, download and save or use previously
    downloaded and saved data. It also allows the use of a static fallback when downloading fails.

    Args:
        downloader (Download): Download object
        fallback_dir (str): Directory containing static fallback data
        saved_dir (str): Directory to save or load downloaded data
        temp_dir (str): Temporary directory for when data is not needed after downloading
        save (bool): Whether to save downloaded data. Defaults to False.
        use_saved (bool): Whether to use saved data. Defaults to False.
    """

    def __init__(
        self,
        downloader,
        fallback_dir,
        saved_dir,
        temp_dir,
        save=False,
        use_saved=False,
    ):
        self.downloader = downloader
        self.fallback_dir = fallback_dir
        self.saved_dir = saved_dir
        self.temp_dir = temp_dir
        self.save = save
        self.use_saved = use_saved
        if save:
            if use_saved:
                raise ValueError(
                    "Either the save or use_saved flags can be set to True!"
                )
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

    def retrieve_file(
        self, url, filename, logstr=None, fallback=False, **kwargs
    ):
        """Retrieve file

        Args:
            url (str): URL to download
            filename (str): Filename to use for saved file
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download_file call

        Returns:
            str: Path to downloaded file

        """
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

    def retrieve_text(
        self, url, filename, logstr=None, fallback=False, **kwargs
    ):
        """Retrieve text

        Args:
            url (str): URL to download
            filename (str): Filename to use for saved file
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download call

        Returns:
            Union[Dict,List]: The text from the file

        """
        if not logstr:
            logstr = filename
        saved_path = join(self.saved_dir, filename)
        if self.use_saved:
            logger.info(f"Using saved {logstr} in {saved_path}")
            text = load_file_to_str(saved_path)
        else:
            try:
                logger.info(
                    f"Downloading {logstr} from {self.get_url_logstr(url)}"
                )
                self.downloader.download(url, **kwargs)
                text = self.downloader.get_text()
                if self.save:
                    logger.info(f"Saving {logstr} in {saved_path}")
                    save_str_to_file(text, saved_path)
            except DownloadError:
                if not fallback:
                    raise
                fallback_path = join(self.fallback_dir, filename)
                logger.exception(
                    f"{logstr} download failed, using static data {fallback_path}!"
                )
                text = load_file_to_str(fallback_path)
        return text

    def retrieve_yaml(
        self, url, filename, logstr=None, fallback=False, **kwargs
    ):
        """Retrieve YAML

        Args:
            url (str): URL to download
            filename (str): Filename to use for saved file
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download call

        Returns:
            Union[Dict,List]: The data from the YAML file

        """
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
                self.downloader.download(url, **kwargs)
                ryaml = self.downloader.get_yaml()
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

    def retrieve_json(
        self, url, filename, logstr=None, fallback=False, **kwargs
    ):
        """Retrieve JSON

        Args:
            url (str): URL to download
            filename (str): Filename to use for saved file
            logstr (Optional[str]): Text to use in log string to describe download. Defaults to filename.
            fallback (bool): Whether to use static fallback if download fails. Defaults to False.
            **kwargs: Parameters to pass to download call

        Returns:
            Union[Dict,List]: The data from the JSON file

        """
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
                self.downloader.download(url, **kwargs)
                rjson = self.downloader.get_json()
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
