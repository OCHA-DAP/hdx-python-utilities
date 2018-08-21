# -*- coding: utf-8 -*-
"""Downloading utilities for urls"""
import hashlib
import logging
from collections import OrderedDict
from os import remove
from os.path import splitext, join, exists
from posixpath import basename
from tempfile import gettempdir
from typing import Optional, Dict, Iterator, Union, List, Any, Tuple

import requests
import tabulator
from requests import Request
from six.moves.urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
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
        extra_params_lookup (str): Lookup key for parameters. If not given assumes parameters are at root of the dict.
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
    def get_path_for_url(url, folder=None, filename=None, overwrite=False):
        # type: (str, Optional[str], Optional[str], bool) -> str
        """Get filename from url and join to provided folder or temporary folder if no folder supplied, ensuring uniqueness

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.

        Returns:
            str: Path of downloaded file

        """
        if not filename:
            urlpath = urlsplit(url).path
            filename = basename(urlpath)
        filename, extension = splitext(filename)
        if not folder:
            folder = gettempdir()
        path = join(folder, '%s%s' % (filename, extension))
        if overwrite:
            try:
                remove(path)
            except OSError:
                pass
        else:
            count = 0
            while exists(path):
                count += 1
                path = join(folder, '%s%d%s' % (filename, count, extension))
        return path

    def get_full_url(self, url):
        # type: (str) -> str
        """Get full url including any additional parameters

        Args:
            url (str): URL for which to get full url

        Returns:
            str: Full url including any additional parameters
        """
        request = Request('GET', url)
        preparedrequest = self.session.prepare_request(request)
        return preparedrequest.url

    @staticmethod
    def get_url_for_get(url, parameters=None):
        # type: (str, Optional[Dict]) -> str
        """Get full url for GET request including parameters

        Args:
            url (str): URL to download
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.

        Returns:
            str: Full url

        """
        spliturl = urlsplit(url)
        getparams = OrderedDict(parse_qsl(spliturl.query))
        if parameters is not None:
            getparams.update(parameters)
        spliturl = spliturl._replace(query=urlencode(getparams))
        return urlunsplit(spliturl)

    @staticmethod
    def get_url_params_for_post(url, parameters=None):
        # type: (str, Optional[Dict]) -> Tuple[str, Dict]
        """Get full url for POST request and all parameters including any in the url

        Args:
            url (str): URL to download
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.

        Returns:
            Tuple[str, Dict]: (Full url, parameters)

        """
        spliturl = urlsplit(url)
        getparams = OrderedDict(parse_qsl(spliturl.query))
        if parameters is not None:
            getparams.update(parameters)
        spliturl = spliturl._replace(query='')
        full_url = urlunsplit(spliturl)
        return full_url, getparams

    def setup(self, url, stream=True, post=False, parameters=None, timeout=None):
        # type: (str, bool, bool, Optional[Dict], Optional[float]) -> requests.Response
        """Setup download from provided url returning the response

        Args:
            url (str): URL to download
            stream (bool): Whether to stream download. Defaults to True.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).

        Returns:
            requests.Response: requests.Response object

        """
        self.close_response()
        self.response = None
        try:
            if post:
                full_url, parameters = self.get_url_params_for_post(url, parameters)
                self.response = self.session.post(full_url, data=parameters, stream=stream, timeout=timeout)
            else:
                self.response = self.session.get(self.get_url_for_get(url, parameters), stream=stream, timeout=timeout)
            self.response.raise_for_status()
        except Exception as e:
            raisefrom(DownloadError, 'Setup of Streaming Download of %s failed!', e)
        return self.response

    def hash_stream(self, url):
        # type: (str) -> str
        """Stream file from url and hash it using MD5. Must call setup method first.

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

    def stream_file(self, url, folder=None, filename=None, overwrite=False):
        # type: (str, Optional[str], Optional[str], bool) -> str
        """Stream file from url and store in provided folder or temporary folder if no folder supplied.
        Must call setup method first.

        Args:
            url (str): URL to download
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.

        Returns:
            str: Path of downloaded file

        """
        path = self.get_path_for_url(url, folder, filename, overwrite)
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

    def download_file(self, url, folder=None, filename=None, overwrite=False,
                      post=False, parameters=None, timeout=None):
        # type: (str, Optional[str], Optional[str], bool, bool, Optional[Dict], Optional[float]) -> str
        """Download file from url and store in provided folder or temporary folder if no folder supplied

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None.
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).

        Returns:
            str: Path of downloaded file

        """
        self.setup(url, stream=True, post=post, parameters=parameters, timeout=timeout)
        return self.stream_file(url, folder, filename, overwrite)

    def download(self, url, post=False, parameters=None, timeout=None):
        # type: (str, bool, Optional[Dict], Optional[float]) -> requests.Response
        """Download url

        Args:
            url (str): URL to download
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).

        Returns:
            requests.Response: Response

        """
        return self.setup(url, stream=False, post=post, parameters=parameters, timeout=timeout)

    def get_json(self):
        # type: () -> Any
        """Get JSON content of download

        Returns:
            Any: JSON content of download

        """
        return self.response.json(object_pairs_hook=OrderedDict)

    def get_tabular_stream(self, url, **kwargs):
        # type: (str, Any) -> tabulator.Stream
        """Get Tabulator stream.

        Args:
            url (str): URL to download
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            tabulator.Stream: Tabulator Stream object

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

    def download_tabular_rows_as_dicts(self, url, headers=1, keycolumn=1, **kwargs):
        # type: (str, Union[int, List[int], List[str]], int, Any) -> Dict[Dict]
        """Download multicolumn csv from url and return dictionary where keys are first column and values are
        dictionaries with keys from column headers and values from columns beneath

        Args:
            url (str): URL to download
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            keycolumn (int): Number of column to be used for key. Defaults to 1.
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
        key_header = headers[keycolumn - 1]
        for row in stream.iter(keyed=True):
            first_val = row[key_header]
            output_dict[first_val] = dict()
            for header in row:
                if header == key_header:
                    continue
                else:
                    output_dict[first_val][header] = row[header]
        return output_dict

    def download_tabular_cols_as_dicts(self, url, headers=1, keycolumn=1, **kwargs):
        # type: (str, Union[int, List[int], List[str]], int, Any) -> Dict[Dict]
        """Download multicolumn csv from url and return dictionary where keys are header names and values are
        dictionaries with keys from first column and values from other columns

        Args:
            url (str): URL to download
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            keycolumn (int): Number of column to be used for key. Defaults to 1.
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
        key_header = headers[keycolumn - 1]
        for header in stream.headers:
            if header == key_header:
                continue
            output_dict[header] = dict()
        for row in stream.iter(keyed=True):
            for header in row:
                if header == key_header:
                    continue
                output_dict[header][row[key_header]] = row[header]
        return output_dict
