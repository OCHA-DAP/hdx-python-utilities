# -*- coding: utf-8 -*-
"""Downloading utilities for urls"""
import hashlib
import logging
from os.path import splitext, join, exists
from posixpath import basename
from tempfile import gettempdir
from typing import Optional, Dict, Iterator, Union, List, Any

import requests
import tabulator
from requests import Request
from six.moves.urllib.parse import urlparse
from tabulator.exceptions import TabulatorException

from hdx.utilities import raisefrom
from hdx.utilities.session import get_session

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


class Download(object):
    """Download class with various download operations. Currently only GET requests are used and supported.

    Args:
        **kwargs: See below
        auth (Tuple[str, str]): Authorisation information in tuple form (user, pass) OR
        basic_auth (str): Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
        basic_auth_file (str): Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
        extra_params_dict (Dict[str, str]): Extra parameters to put on end of url as a dictionary OR
        extra_params_json (str): Path to JSON file containing extra parameters to put on end of url OR
        extra_params_yaml (str): Path to YAML file containing extra parameters to put on end of url
        status_forcelist (List[int]): HTTP statuses for which to force retry
        method_whitelist (iterable): HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.session = get_session(**kwargs)
        self.response = None

    def close_response(self):
        # type: () -> None
        """Close response

        Returns:
            None

        """
        if self.response:
            try:
                self.response.close()
            except Exception:
                pass

    def close(self):
        # type: () -> None
        """Close response and session

        Returns:
            None

        """
        self.close_response()
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @staticmethod
    def get_path_for_url(url, folder=None, filename=None):
        # type: (str, Optional[str], Optional[str]) -> str
        """Get filename from url and join to provided folder or temporary folder if no folder supplied, ensuring uniqueness

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).

        Returns:
            str: Path of downloaded file

        """
        if not filename:
            urlpath = urlparse(url).path
            filename = basename(urlpath)
        filename, extension = splitext(filename)
        if not folder:
            folder = gettempdir()
        path = join(folder, '%s%s' % (filename, extension))
        count = 0
        while exists(path):
            count += 1
            path = join(folder, '%s%d%s' % (filename, count, extension))
        return path

    def get_full_url(self, url):
        # type: () -> str
        """Get full url including any additional parameters

        Returns:
            str: Full url including any additional parameters
        """
        request = Request('GET', url)
        preparedrequest = self.session.prepare_request(request)
        return preparedrequest.url

    def setup_stream(self, url, timeout=None):
        # type: (str, Optional[float]) -> None
        """Setup streaming download from provided url

        Args:
            url (str): URL to download
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).


        """
        self.close_response()
        self.response = None
        try:
            self.response = self.session.get(url, stream=True, timeout=timeout)
            self.response.raise_for_status()
        except Exception as e:
            raisefrom(DownloadError, 'Setup of Streaming Download of %s failed!', e)

    def hash_stream(self, url):
        # type: (str) -> str
        """Stream file from url and hash it using MD5. Must call setup_streaming_download method first.

        Args:
            url (str): URL to download

        Returns:
            str: MD5 hash of file

        """
        md5hash = hashlib.md5()
        try:
            for chunk in self.response.iter_content(chunk_size=10240):
                if chunk:  # filter out keep-alive new chunks
                    md5hash.update(chunk)
            return md5hash.hexdigest()
        except Exception as e:
            raisefrom(DownloadError, 'Download of %s failed in retrieval of stream!' % url, e)

    def stream_file(self, url, folder=None, filename=None):
        # type: (str, Optional[str], Optional[str]) -> str
        """Stream file from url and store in provided folder or temporary folder if no folder supplied.
        Must call setup_streaming_download method first.

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).

        Returns:
            str: Path of downloaded file

        """
        path = self.get_path_for_url(url, folder, filename)
        f = None
        try:
            f = open(path, 'wb')
            for chunk in self.response.iter_content(chunk_size=10240):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            return f.name
        except Exception as e:
            raisefrom(DownloadError, 'Download of %s failed in retrieval of stream!' % url, e)
        finally:
            if f:
                f.close()

    def download_file(self, url, folder=None, filename=None, timeout=None):
        # type: (str, Optional[str], Optional[str], Optional[float]) -> str
        """Download file from url and store in provided folder or temporary folder if no folder supplied

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None.
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).

        Returns:
            str: Path of downloaded file

        """
        self.setup_stream(url, timeout)
        return self.stream_file(url, folder, filename)

    def download(self, url, timeout=None):
        # type: (str, Optional[float]) -> requests.Response
        """Download url

        Args:
            url (str): URL to download
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).

        Returns:
            requests.Response: Response

        """
        self.close_response()
        try:
            self.response = self.session.get(url, timeout=timeout)
            self.response.raise_for_status()
        except Exception as e:
            raisefrom(DownloadError, 'Download of %s failed!' % url, e)
        return self.response

    def get_tabular_stream(self, url, **kwargs):
        # type: (str, Any) -> tabulator.Stream
        """Get iterator for reading rows from tabular data. Each row is returned as a dictionary.

        Args:
            url (str): URL to download
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            tabulator.Stream: Tabulator Stream object.

        """
        self.close_response()
        file_type = kwargs.get('file_type')
        if file_type is not None:
            kwargs['format'] = file_type
            del kwargs['file_type']
        try:
            self.response = tabulator.Stream(url, **kwargs)
            self.response.open()
            return self.response
        except TabulatorException as e:
            raisefrom(DownloadError, 'Getting tabular stream for %s failed!' % url, e)

    def get_tabular_rows(self, url, dict_rows=False, **kwargs):
        # type: (str, bool, Any) -> Iterator[Dict]
        """Get iterator for reading rows from tabular data. Each row is returned as a dictionary.

        Args:
            url (str): URL to download
            dict_rows (bool): Return dict (requires headers parameter) or list for each row. Defaults to False (list).
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Iterator[Union[List,Dict]]: Iterator where each row is returned as a list or dictionary.

        """
        return self.get_tabular_stream(url, **kwargs).iter(keyed=dict_rows)

    def download_tabular_key_value(self, url, **kwargs):
        # type: (str, Any) -> Dict
        """Download 2 column csv from url and return a dictionary of keys (first column) and values (second column)

        Args:
            url (str): URL to download
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Dict: Dictionary keys (first column) and values (second column)

        """
        output_dict = dict()
        for row in self.get_tabular_rows(url, **kwargs):
            if len(row) < 2:
                continue
            output_dict[row[0]] = row[1]
        return output_dict

    def download_tabular_rows_as_dicts(self, url, headers=1, **kwargs):
        # type: (str, Union[int, List[int], List[str]], Any) -> Dict[Dict]
        """Download multicolumn csv from url and return dictionary where keys are first column and values are
        dictionaries with keys from column headers and values from columns beneath

        Args:
            url (str): URL to download
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            **kwargs:
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Dict[Dict]: Dictionary where keys are first column and values are dictionaries with keys from column
            headers and values from columns beneath

        """
        kwargs['headers'] = headers
        stream = self.get_tabular_stream(url, **kwargs)
        output_dict = dict()
        headers = stream.headers
        first_header = headers[0]
        for row in stream.iter(keyed=True):
            first_val = row[first_header]
            output_dict[first_val] = dict()
            for header in row:
                if header == first_header:
                    continue
                else:
                    output_dict[first_val][header] = row[header]
        return output_dict

    def download_tabular_cols_as_dicts(self, url, headers=1, **kwargs):
        # type: (str, Union[int, List[int], List[str]], Any) -> Dict[Dict]
        """Download multicolumn csv from url and return dictionary where keys are header names and values are
        dictionaries with keys from first column and values from other columns

        Args:
            url (str): URL to download
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            **kwargs:
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Dict[Dict]: Dictionary where keys are header names and values are dictionaries with keys from first column
            and values from other columns

        """
        kwargs['headers'] = headers
        stream = self.get_tabular_stream(url, **kwargs)
        output_dict = dict()
        headers = stream.headers
        first_header = headers[0]
        for header in stream.headers:
            if header == first_header:
                continue
            output_dict[header] = dict()
        for row in stream.iter(keyed=True):
            for header in row:
                if header == first_header:
                    continue
                output_dict[header][row[first_header]] = row[header]
        return output_dict
