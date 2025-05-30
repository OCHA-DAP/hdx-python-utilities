"""Downloading utilities for urls."""

import hashlib
import logging
from copy import deepcopy
from os import remove
from os.path import exists, isfile, join, split, splitext
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from frictionless import FrictionlessException
from frictionless.resources import TableResource
from ratelimit import RateLimitDecorator, sleep_and_retry
from requests import Request
from ruamel.yaml import YAML
from xlsx2csv import Xlsx2csv

from .base_downloader import BaseDownload, DownloadError
from .frictionless_wrapper import get_frictionless_tableresource
from .path import get_filename_from_url, get_temp_dir
from .session import get_session
from .typehint import ListDict, ListTuple

logger = logging.getLogger(__name__)


class Download(BaseDownload):
    """Download class with various download operations. Requires either global
    user agent to be set or appropriate user agent parameter(s) to be
    completed.

    Args:
        user_agent (Optional[str]): User agent string. HDXPythonUtilities/X.X.X- is prefixed.
        user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yaml.
        user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.
        use_env (bool): Whether to read environment variables. Defaults to True.
        fail_on_missing_file (bool): Raise an exception if any specified configuration files are missing. Defaults to True.
        verify (bool): Whether to verify SSL certificates. Defaults to True.
        rate_limit (Optional[Dict]): Rate limiting per host eg. {"calls": 1, "period": 0.1}. Defaults to None.
        **kwargs: See below
        auth (Tuple[str, str]): Authorisation information in tuple form (user, pass) OR
        basic_auth (str): Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
        basic_auth_file (str): Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
        bearer_token (str): Bearer token string OR
        bearer_token_file (str): Path to file containing bearer token string OR
        extra_params_dict (Dict[str, str]): Extra parameters to put on end of url as a dictionary OR
        extra_params_json (str): Path to JSON file containing extra parameters to put on end of url OR
        extra_params_yaml (str): Path to YAML file containing extra parameters to put on end of url
        extra_params_lookup (str): Lookup key for parameters. If not given assumes parameters are at root of the dict.
        headers (Dict): Additional headers to add to request.
        use_auth (str): If more than one auth found, specify which one to use, rather than failing.
        status_forcelist (ListTuple[int]): HTTP statuses for which to force retry
        allowed_methods (iterable): HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).
    """

    downloaders = {}

    def __init__(
        self,
        user_agent: Optional[str] = None,
        user_agent_config_yaml: Optional[str] = None,
        user_agent_lookup: Optional[str] = None,
        use_env: bool = True,
        fail_on_missing_file: bool = True,
        verify: bool = True,
        rate_limit: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        session = kwargs.get("session")
        if session:
            self.session = session
        else:
            self.session = get_session(
                user_agent,
                user_agent_config_yaml,
                user_agent_lookup,
                use_env,
                fail_on_missing_file,
                verify,
                **kwargs,
            )
        self.response = None
        if rate_limit is not None:
            self.setup = sleep_and_retry(
                RateLimitDecorator(
                    calls=rate_limit["calls"], period=rate_limit["period"]
                ).__call__(self.normal_setup)
            )
        else:
            self.setup = self.normal_setup

    def close_response(self) -> None:
        """Close response.

        Returns:
            None
        """
        if self.response:
            try:
                self.response.close()
            except Exception:
                pass

    def close(self) -> None:
        """Close response and session.

        Returns:
            None
        """
        self.close_response()
        self.session.close()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Allow usage of with.

        Args:
            exc_type (Any): Exception type
            exc_value (Any): Exception value
            traceback (Any): Traceback

        Returns:
            None
        """
        self.close()

    @staticmethod
    def get_path_for_url(
        url: str,
        folder: Optional[str] = None,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        overwrite: bool = False,
        keep: bool = False,
    ) -> str:
        """Get filename from url and join to provided folder or temporary
        folder if no folder supplied, ensuring uniqueness.

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            path (Optional[str]): Full path to use for downloaded file. Defaults to None (use folder and filename).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.
            keep (bool): Whether to keep already downloaded file. Defaults to False.

        Returns:
            str: Path of downloaded file
        """
        if path:
            if folder or filename:
                raise DownloadError(
                    "Cannot use folder or filename and path arguments together!"
                )
            folder, filename = split(path)
        if not filename:
            filename = get_filename_from_url(url)
        filename, extension = splitext(filename)
        if not folder:
            folder = get_temp_dir()
        path = join(folder, f"{filename}{extension}")
        if overwrite:
            try:
                remove(path)
            except OSError:
                pass
        elif not keep:
            count = 0
            while exists(path):
                count += 1
                path = join(folder, f"{filename}{count}{extension}")
        return path

    def get_full_url(self, url: str) -> str:
        """Get full url including any additional parameters.

        Args:
            url (str): URL for which to get full url

        Returns:
            str: Full url including any additional parameters
        """
        request = Request("GET", url)
        preparedrequest = self.session.prepare_request(request)
        return preparedrequest.url

    @staticmethod
    def get_url_for_get(url: str, parameters: Optional[Dict] = None) -> str:
        """Get full url for GET request including parameters.

        Args:
            url (str): URL to download
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.

        Returns:
            str: Full url
        """
        spliturl = urlsplit(url)
        getparams = dict(parse_qsl(spliturl.query))
        if parameters is not None:
            getparams.update(parameters)
        spliturl = spliturl._replace(query=urlencode(getparams))
        return urlunsplit(spliturl)

    @staticmethod
    def get_url_params_for_post(
        url: str, parameters: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """Get full url for POST request and all parameters including any in
        the url.

        Args:
            url (str): URL to download
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.

        Returns:
            Tuple[str, Dict]: (Full url, parameters)
        """
        spliturl = urlsplit(url)
        getparams = dict(parse_qsl(spliturl.query))
        if parameters is not None:
            getparams.update(parameters)
        spliturl = spliturl._replace(query="")
        full_url = urlunsplit(spliturl)
        return full_url, getparams

    @staticmethod
    def hxl_row(
        headers: ListTuple[str],
        hxltags: Dict[str, str],
        dict_form: bool = False,
    ) -> Union[List[str], Dict[str, str]]:
        """Return HXL tag row for header row given list of headers and
        dictionary with header to HXL hashtag mappings. Return list or
        dictionary depending upon the dict_form argument.

        Args:
            headers (ListTuple[str]): Headers for which to get HXL hashtags
            hxltags (Dict[str,str]): Header to HXL hashtag mapping
            dict_form (bool): Return dict or list. Defaults to False (list)

        Returns:
            Union[List[str],Dict[str,str]]: Return either a list or dictionary conating HXL hashtags
        """
        if dict_form:
            return {header: hxltags.get(header, "") for header in headers}
        return [hxltags.get(header, "") for header in headers]

    def normal_setup(
        self,
        url: str,
        stream: bool = True,
        post: bool = False,
        parameters: Optional[Dict] = None,
        timeout: Optional[float] = None,
        headers: Optional[Dict] = None,
        encoding: Optional[str] = None,
    ) -> requests.Response:
        """Setup download from provided url returning the response.

        Args:
            url (str): URL or path to download
            stream (bool): Whether to stream download. Defaults to True.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Optional[Dict]): Headers to pass. Defaults to None.
            encoding (Optional[str]): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            requests.Response: requests.Response object
        """
        self.close_response()
        self.response = None
        try:
            spliturl = urlsplit(url)
            if not spliturl.scheme:
                if isfile(url):
                    url = Path(url).resolve().as_uri()
                else:
                    spliturl = spliturl._replace(scheme="https")
                    url = urlunsplit(spliturl)
            if post:
                full_url, parameters = self.get_url_params_for_post(url, parameters)
                self.response = self.session.post(
                    full_url,
                    data=parameters,
                    stream=stream,
                    timeout=timeout,
                    headers=headers,
                )
            else:
                self.response = self.session.get(
                    self.get_url_for_get(url, parameters),
                    stream=stream,
                    timeout=timeout,
                    headers=headers,
                )
            self.response.raise_for_status()
            if encoding:
                self.response.encoding = encoding
        except Exception as e:
            raise DownloadError(f"Setup of Streaming Download of {url} failed!") from e
        return self.response

    def set_bearer_token(self, bearer_token: str) -> None:
        """Set bearer token

        Args:
            bearer_token (str): Bearer token

        Returns:
            None
        """
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {bearer_token}",
            }
        )

    def hash_stream(self, url: str) -> str:
        """Stream file from url and hash it using MD5. Must call setup method
        first.

        Args:
            url (str): URL or path to download

        Returns:
            str: MD5 hash of file
        """
        md5hash = hashlib.md5()
        try:
            for chunk in self.response.iter_content(chunk_size=10240):
                if chunk:  # filter out keep-alive new chunks
                    md5hash.update(chunk)
            return md5hash.hexdigest()
        except Exception:
            raise DownloadError(
                f"Download of {url} failed in retrieval of stream!" % url
            )

    def stream_path(self, path: str, errormsg: str):
        """Stream file from url and store in provided path. Must call setup
        method first.

        Args:
            path (str): Path for downloaded file
            errormsg (str): Error message to display if there is a problem

        Returns:
            str: Path of downloaded file
        """
        f = None
        try:
            f = open(path, "wb")
            for chunk in self.response.iter_content(chunk_size=10240):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            return f.name
        except Exception as e:
            raise DownloadError(errormsg) from e
        finally:
            if f:
                f.close()

    def stream_file(
        self,
        url: str,
        folder: Optional[str] = None,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        overwrite: bool = False,
        keep: bool = False,
    ) -> str:
        """Stream file from url and store in provided folder or temporary
        folder if no folder supplied. Must call setup method first.

        Args:
            url (str): URL or path to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            path (Optional[str]): Full path to use for downloaded file. Defaults to None (use folder and filename).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.
            keep (bool): Whether to keep already downloaded file. Defaults to False.

        Returns:
            str: Path of downloaded file
        """
        path = self.get_path_for_url(url, folder, filename, path, overwrite, keep)
        if keep and exists(path):
            return path
        return self.stream_path(
            path, f"Download of {url} failed in retrieval of stream!"
        )

    def download_file(
        self,
        url: str,
        **kwargs: Any,
    ) -> str:
        """Download file from url and store in provided folder or temporary
        folder if no folder supplied.

        Args:
            url (str): URL or path to download
            **kwargs: See below
            folder (str): Folder to download it to. Defaults to temporary folder.
            filename (str): Filename to use for downloaded file. Defaults to deriving from url.
            path (str): Full path to use for downloaded file instead of folder and filename.
            overwrite (bool): Whether to overwrite existing file. Defaults to False.
            keep (bool): Whether to keep already downloaded file. Defaults to False.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            str: Path of downloaded file
        """
        folder = kwargs.get("folder")
        filename = kwargs.get("filename")
        path = kwargs.get("path")
        overwrite = kwargs.get("overwrite", False)
        keep = kwargs.get("keep", False)
        path = self.get_path_for_url(url, folder, filename, path, overwrite, keep)
        if keep and exists(path):
            return path
        self.setup(
            url,
            stream=True,
            post=kwargs.get("post", False),
            parameters=kwargs.get("parameters"),
            timeout=kwargs.get("timeout"),
            headers=kwargs.get("headers"),
            encoding=kwargs.get("encoding"),
        )
        return self.stream_path(
            path, f"Download of {url} failed in retrieval of stream!"
        )

    def download(self, url: str, **kwargs: Any) -> requests.Response:
        """Download url.

        Args:
            url (str): URL or path to download
            **kwargs: See below
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            requests.Response: Response
        """
        return self.setup(
            url,
            stream=False,
            post=kwargs.get("post", False),
            parameters=kwargs.get("parameters"),
            timeout=kwargs.get("timeout"),
            headers=kwargs.get("headers"),
            encoding=kwargs.get("encoding"),
        )

    def get_header(self, header: str) -> Any:
        """Get a particular response header of download.

        Args:
            header (str): Header for which to get value

        Returns:
            Any: Response header's value
        """
        return self.response.headers.get(header)

    def get_headers(self) -> Any:
        """Get response headers of download.

        Returns:
            Any: Response headers
        """
        return self.response.headers

    def get_status(self) -> int:
        """Get response status code.

        Returns:
            int: Response status code
        """
        return self.response.status_code

    def get_text(self) -> str:
        """Get text content of download.

        Returns:
            str: Text content of download
        """
        return self.response.text

    def get_yaml(self) -> Any:
        """Get YAML content of download.

        Returns:
            Any: YAML content of download
        """
        with YAML() as yaml:
            return yaml.load(self.response.text)

    def get_json(self) -> Any:
        """Get JSON content of download.

        Returns:
            Any: JSON content of download
        """
        return self.response.json()

    def download_text(self, url: str, **kwargs: Any) -> str:
        """Download url as text.

        Args:
            url (str): URL or path to download
            **kwargs: See below
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            str: Text content of download
        """
        self.download(url, **kwargs)
        return self.get_text()

    def download_yaml(self, url: str, **kwargs: Any) -> Any:
        """Download url as YAML.

        Args:
            url (str): URL or path to download
            **kwargs: See below
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            str: YAML content of download
        """
        self.download(url, **kwargs)
        return self.get_yaml()

    def download_json(self, url: str, **kwargs: Any) -> Any:
        """Download url as JSON.

        Args:
            url (str): URL or path to download
            **kwargs: See below
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Dict): Parameters to pass. Defaults to None.
            timeout (float): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Dict): Headers to pass. Defaults to None.
            encoding (str): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            str: JSON content of download
        """
        self.download(url, **kwargs)
        return self.get_json()

    def get_frictionless_tableresource(
        self,
        url: str,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        **kwargs: Any,
    ) -> TableResource:
        """Get Frictionless TableResource.

        Args:
            url (str): URL or path to download
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            **kwargs:
            has_header (bool): Whether data has a header. Defaults to True.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            TableResource: frictionless TableResource object
        """
        self.close_response()
        try:
            self.response = get_frictionless_tableresource(
                url, ignore_blank_rows, infer_types, self.session, **kwargs
            )
        except FrictionlessException as e:
            raise DownloadError(str(e)) from e
        return self.response

    def _get_tabular_rows(
        self,
        url: str,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        dict_form: bool = False,
        include_headers: bool = False,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Tuple[List[str], Iterator[ListDict]]:
        """Returns header of tabular file pointed to by url and an iterator
        where each row is returned as a list or dictionary depending on the
        dict_form argument. The headers argument is either a row number or list
        of row numbers (in case of multi-line headers) to be considered as
        headers (rows start counting at 1), or the actual headers defined as a
        list of strings. It defaults to 1 and cannot be None. The dict_form
        arguments specifies if each row should be returned as a dictionary or a
        list, defaulting to a list.

        Optionally, headers can be inserted at specific positions. This is achieved blah blah blah blah blah blah
        using the header_insertions argument. If supplied, it is a list of tuples of the
        form (position, header) to be inserted. A function is called for each row. If
        supplied, it takes as arguments: headers (prior to any insertions) and row
        (which will be in dict or list form depending upon the dict_rows argument) and
        outputs a modified row or None to ignore the row.

        Args:
            url (str): URL or path to read from
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form (bool): Return dict or list for each row. Defaults to False (list)
            include_headers (bool): Whether to include headers in iterator. Defaults to False.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            xlsx2csv (bool): Whether to convert xlsx files. Defaults to False.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Tuple[List[str],Iterator[ListDict]]: Tuple (headers, iterator where each row is a list or dictionary)
        """
        if headers is None:
            raise DownloadError("Argument headers cannot be None!")
        xlsx2csv = kwargs.pop("xlsx2csv", False)
        if xlsx2csv:
            path = self.download_file(url)
            outpath = path.replace(".xlsx", ".csv")
            sheet = kwargs.pop("sheet", 1)
            if isinstance(sheet, int):
                sheet_args = {"sheetid": sheet}
            else:
                sheet_args = {"sheetname": sheet}
            Xlsx2csv(path).convert(outpath, **sheet_args)
            url = outpath
            kwargs["format"] = "csv"  # format takes precedence over file_type
            kwargs.pop("fill_merged_cells", None)

        resource = self.get_frictionless_tableresource(
            url,
            ignore_blank_rows=ignore_blank_rows,
            infer_types=infer_types,
            headers=headers,
            **kwargs,
        )
        origheaders = resource.header
        if header_insertions is None or origheaders is None:
            headers = origheaders
        else:
            headers = deepcopy(origheaders)
            for position, header in header_insertions:
                headers.insert(position, header)

        def get_next():
            if include_headers:
                yield headers
            for inrow in resource.row_stream:
                if dict_form:
                    row = inrow.to_dict()
                else:
                    row = inrow.to_list()
                if row_function:
                    processed_row = row_function(origheaders, row)
                    if processed_row is not None:
                        if dict_form:
                            processed_row = processed_row
                        yield processed_row
                else:
                    yield row

        return headers, get_next()

    def get_tabular_rows(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        dict_form: bool = False,
        include_headers: bool = False,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Tuple[List[str], Iterator[ListDict]]:
        """Returns header of tabular file(s) pointed to by url and an iterator
        where each row is returned as a list or dictionary depending on the
        dict_rows argument.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1. The dict_form
        argument specifies if each row should be returned as a dictionary or a list,
        defaulting to a list.

        Optionally, headers can be inserted at specific positions. This is achieved
        using the header_insertions argument. If supplied, it is a list of tuples of the
        form (position, header) to be inserted. A function is called for each row. If
        supplied, it takes as arguments: headers (prior to any insertions) and row
        (which will be in dict or list form depending upon the dict_rows argument) and
        outputs a modified row or None to ignore the row.

        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form (bool): Return dict or list for each row. Defaults to False (list)
            include_headers (bool): Whether to include headers in iterator. Defaults to False.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            xlsx2csv (bool): Whether to convert xlsx files. Defaults to False.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Tuple[List[str],Iterator[ListDict]]: Tuple (headers, iterator where each row is a list or dictionary)
        """
        if isinstance(url, list):
            is_list = True
            orig_kwargs = deepcopy(kwargs)
            urls = url
            url = urls[0]
        else:
            is_list = False
        outheaders, iterator1 = self._get_tabular_rows(
            url,
            headers,
            dict_form,
            include_headers,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        if not is_list:
            return outheaders, iterator1

        def make_iterator():
            yield from iterator1
            for url in urls[1:]:
                temp_kwargs = deepcopy(orig_kwargs)
                _, iterator = self._get_tabular_rows(
                    url,
                    headers,
                    dict_form,
                    include_headers,
                    ignore_blank_rows,
                    infer_types,
                    header_insertions,
                    row_function,
                    **temp_kwargs,
                )
                if has_hxl:
                    next(iterator)
                yield from iterator

        return outheaders, make_iterator()

    def get_tabular_rows_as_list(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        include_headers: bool = True,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Tuple[List[str], Iterator[List]]:
        """Returns headers and an iterator where each row is returned as a
        list.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1 and cannot be
        None.

        Optionally, headers can be inserted at specific positions. This is
        achieved using the header_insertions argument. If supplied, it is a list of
        tuples of the form (position, header) to be inserted. A function is called for
        each row. If supplied, it takes as arguments: headers (prior to any insertions)
        and row (which will be in dict or list form depending upon the dict_rows
        argument) and outputs a modified row or None to ignore the row.

        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            include_headers (bool): Whether to include headers in iterator. Defaults to True.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            xlsx2csv (bool): Whether to convert xlsx files. Defaults to False.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Tuple[List[str],Iterator[List]]: Tuple (headers, iterator where each row is a list)
        """

        headers, iterator = self.get_tabular_rows(
            url,
            has_hxl,
            headers,
            False,
            include_headers,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        return headers, iterator

    def get_tabular_rows_as_dict(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Tuple[List[str], Iterator[Dict]]:
        """Returns headers and an iterator where each row is returned as a
        dictionary.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1 and cannot be
        None.

        Optionally, headers can be inserted at specific positions. This is
        achieved using the header_insertions argument. If supplied, it is a list of
        tuples of the form (position, header) to be inserted. A function is called for
        each row. If supplied, it takes as arguments: headers (prior to any insertions)
        and row (which will be in dict or list form depending upon the dict_rows
        argument) and outputs a modified row or None to ignore the row.

        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            xlsx2csv (bool): Whether to convert xlsx files. Defaults to False.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Tuple[List[str], Iterator[Dict]]: Tuple (headers, iterator where each row is a dictionary)
        """

        headers, iterator = self.get_tabular_rows(
            url,
            has_hxl,
            headers,
            True,
            False,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        return headers, iterator

    def download_tabular_key_value(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        include_headers: bool = True,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Dict:
        """Download 2 column csv from url and return a dictionary of keys
        (first column) and values (second column).

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1 and cannot be
        None.

        Optionally, headers can be inserted at specific positions. This is
        achieved using the header_insertions argument. If supplied, it is a list of
        tuples of the form (position, header) to be inserted. A function is called for
        each row. If supplied, it takes as arguments: headers (prior to any insertions)
        and row (which will be in dict or list form depending upon the dict_rows
        argument) and outputs a modified row or None to ignore the row.


        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            include_headers (bool): Whether to include headers in iterator. Defaults to True.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""]
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Dict: Dictionary keys (first column) and values (second column)
        """
        output_dict = {}
        _, rows = self.get_tabular_rows_as_list(
            url,
            has_hxl,
            headers,
            include_headers,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        for row in rows:
            if len(row) < 2:
                continue
            output_dict[row[0]] = row[1]
        return output_dict

    def download_tabular_rows_as_dicts(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        keycolumn: int = 1,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Dict[str, Dict]:
        """Download multicolumn csv from url and return dictionary where keys
        are first column and values are dictionaries with keys from column
        headers and values from columns beneath.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1 and cannot be
        None.

        Optionally, headers can be inserted at specific positions. This is
        achieved using the header_insertions argument. If supplied, it is a list of
        tuples of the form (position, header) to be inserted. A function is called for
        each row. If supplied, it takes as arguments: headers (prior to any insertions)
        and row (which will be in dict or list form depending upon the dict_rows
        argument) and outputs a modified row or None to ignore the row.

        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            keycolumn (int): Number of column to be used for key. Defaults to 1.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Dict[str,Dict]: Dictionary where keys are first column and values are dictionaries with keys from column
            headers and values from columns beneath
        """
        headers, iterator = self.get_tabular_rows_as_dict(
            url,
            has_hxl,
            headers,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        output_dict = {}
        key_header = headers[keycolumn - 1]
        for row in iterator:
            first_val = row[key_header]
            output_dict[first_val] = {}
            for header in row:
                if header == key_header:
                    continue
                output_dict[first_val][header] = row[header]
        return output_dict

    def download_tabular_cols_as_dicts(
        self,
        url: Union[str, ListTuple[str]],
        has_hxl: bool = False,
        headers: Union[int, ListTuple[int], ListTuple[str]] = 1,
        keycolumn: int = 1,
        ignore_blank_rows: bool = True,
        infer_types: bool = False,
        header_insertions: Optional[ListTuple[Tuple[int, str]]] = None,
        row_function: Optional[Callable[[List[str], ListDict], ListDict]] = None,
        **kwargs: Any,
    ) -> Dict[str, Dict]:
        """Download multicolumn csv from url and return dictionary where keys
        are header names and values are dictionaries with keys from first
        column and values from other columns.

        When a list of urls is supplied (in url), then the has_hxl flag indicates if the
        files are HXLated so that the HXL row is only included from the first file.
        The headers argument is either a row number or list of row numbers (in case of
        multi-line headers) to be considered as headers (rows start counting at 1), or
        the actual headers defined as a list of strings. It defaults to 1 and cannot be
        None.

        Optionally, headers can be inserted at specific positions. This is
        achieved using the header_insertions argument. If supplied, it is a list of
        tuples of the form (position, header) to be inserted. A function is called for
        each row. If supplied, it takes as arguments: headers (prior to any insertions)
        and row (which will be in dict or list form depending upon the dict_rows
        argument) and outputs a modified row or None to ignore the row.

        Args:
            url (Union[str, ListTuple[str]]): A single or list of URLs or paths to read from
            has_hxl (bool): Whether files have HXL hashtags. Ignored for single url. Defaults to False.
            headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            keycolumn (int): Number of column to be used for key. Defaults to 1.
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            infer_types (bool): Whether to infer types. Defaults to False (strings).
            header_insertions (Optional[ListTuple[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],ListDict],ListDict]]): Function to call for each row. Defaults to None.
            **kwargs:
            format (Optional[str]): Type of file. Defaults to inferring.
            file_type (Optional[str]): Type of file. Defaults to inferring.
            encoding (Optional[str]): Type of encoding. Defaults to inferring.
            compression (Optional[str]): Type of compression. Defaults to inferring.
            delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
            skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
            sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
            fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
            http_session (Session): Session object to use. Defaults to downloader session.
            columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
            default_type (Optional[str]): Default field type if infer_types False. Defaults to string.
            float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
            null_values (List[Any]): Values that will return None. Defaults to [""].
            dialect (Dialect): This can be set to override the above. See Frictionless docs.
            detector (Detector): This can be set to override the above. See Frictionless docs.
            layout (Layout): This can be set to override the above. See Frictionless docs.
            schema (Schema): This can be set to override the above. See Frictionless docs.

        Returns:
            Dict[str,Dict]: Dictionary where keys are header names and values are dictionaries with keys from first column
            and values from other columns
        """
        headers, iterator = self.get_tabular_rows_as_dict(
            url,
            has_hxl,
            headers,
            ignore_blank_rows,
            infer_types,
            header_insertions,
            row_function,
            **kwargs,
        )
        output_dict = {}
        key_header = headers[keycolumn - 1]
        for header in headers:
            if header == key_header:
                continue
            output_dict[header] = {}
        for row in iterator:
            for header in row:
                if header == key_header:
                    continue
                output_dict[header][row[key_header]] = row[header]
        return output_dict

    @staticmethod
    def get_column_positions(headers: ListTuple[str]) -> Dict[str, int]:
        """Get mapping of headers to column positions.

        Args:
            headers (ListTuple[str]): List of headers

        Returns:
            Dict[str,int]: Dictionary where keys are header names and values are header positions
        """
        columnpositions = {}
        for i, header in enumerate(headers):
            columnpositions[header] = i
        return columnpositions

    @classmethod
    def generate_downloaders(
        cls,
        custom_configs: Dict[str, Dict],
        user_agent: Optional[str] = None,
        user_agent_config_yaml: Optional[str] = None,
        user_agent_lookup: Optional[str] = None,
        use_env: bool = True,
        fail_on_missing_file: bool = True,
        rate_limit: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        """Generate downloaders. Requires either global user agent to be set or
        appropriate user agent parameter(s) to be completed. The custom_configs
        dictionary is a mapping from name to a dictionary of custom
        configuration parameters that is added to the underlying session's
        params or headers. It can have keys that correspond to the input
        arguments of Download's constructor __init__ (or the other arguments of
        this method).

        Args:
            custom_configs (Dict[str, Dict]): Optional dictionary of custom configurations.
            user_agent (Optional[str]): User agent string. HDXPythonUtilities/X.X.X- is prefixed.
            user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yaml.
            user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.
            use_env (bool): Whether to read environment variables. Defaults to True.
            fail_on_missing_file (bool): Raise an exception if any specified configuration files are missing. Defaults to True.
            rate_limit (Optional[Dict]): Rate limiting per host eg. {"calls": 1, "period": 0.1}. Defaults to None.
            **kwargs: See below
            auth (Tuple[str, str]): Authorisation information in tuple form (user, pass) OR
            basic_auth (str): Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
            basic_auth_file (str): Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
            bearer_token (str): Bearer token string OR
            bearer_token_file (str): Path to file containing bearer token string OR
            extra_params_dict (Dict[str, str]): Extra parameters to put on end of url as a dictionary OR
            extra_params_json (str): Path to JSON file containing extra parameters to put on end of url OR
            extra_params_yaml (str): Path to YAML file containing extra parameters to put on end of url
            extra_params_lookup (str): Lookup key for parameters. If not given assumes parameters are at root of the dict.
            headers (Dict): Additional headers to add to request.
            use_auth (str): If more than one auth found, specify which one to use, rather than failing.
            status_forcelist (ListTuple[int]): HTTP statuses for which to force retry. Defaults to (429, 500, 502, 503, 504).
            allowed_methods (ListTuple[str]): HTTP methods for which to force retry. Defaults to ("HEAD", "TRACE", "GET", "PUT", "OPTIONS", "DELETE").

        Returns:
            None
        """
        kwargs["user_agent"] = user_agent
        kwargs["user_agent_config_yaml"] = user_agent_config_yaml
        kwargs["user_agent_lookup"] = user_agent_lookup
        kwargs["use_env"] = use_env
        kwargs["fail_on_missing_file"] = fail_on_missing_file
        kwargs["rate_limit"] = rate_limit

        cls.downloaders = {"default": cls(**kwargs)}
        for name in custom_configs:
            args_copy = deepcopy(kwargs)
            args_copy.update(custom_configs[name])
            cls.downloaders[name] = cls(**args_copy)

    @classmethod
    def get_downloader(cls, name: Optional[str] = None) -> "Download":
        """Get a generated downloader given a name. If name is not supplied,
        the default one will be returned.

        Args:
            name (Optional[str]): Name of downloader. Defaults to None (get default).

        Returns:
            Download: Downloader object
        """
        return cls.downloaders.get(name, cls.downloaders["default"])
