# -*- coding: utf-8 -*-
"""Downloading utilities for urls"""
import copy
import hashlib
import logging
from collections import OrderedDict
from os import remove
from os.path import splitext, join, exists, isfile, split
from pathlib import Path
from posixpath import basename
from typing import Optional, Dict, Iterator, Union, List, Any, Tuple, Callable

import requests
import tabulator
from ratelimit import sleep_and_retry, RateLimitDecorator
from requests import Request
from ruamel.yaml import YAML
from six.moves.urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from hdx.utilities import raisefrom
from hdx.utilities.path import get_temp_dir
from hdx.utilities.session import get_session

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


class Download(object):
    """Download class with various download operations. Requires either global user agent to be set or appropriate
    user agent parameter(s) to be completed.

    Args:
        user_agent (Optional[str]): User agent string. HDXPythonUtilities/X.X.X- is prefixed.
        user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
        user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.
        use_env (bool): Whether to read environment variables. Defaults to True.
        fail_on_missing_file (bool): Raise an exception if any specified configuration files are missing. Defaults to True.
        rate_limit (Optional[Dict]): Rate limiting to use as a dict with calls and period. Defaults to None.
        **kwargs: See below
        auth (Tuple[str, str]): Authorisation information in tuple form (user, pass) OR
        basic_auth (str): Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
        basic_auth_file (str): Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
        extra_params_dict (Dict[str, str]): Extra parameters to put on end of url as a dictionary OR
        extra_params_json (str): Path to JSON file containing extra parameters to put on end of url OR
        extra_params_yaml (str): Path to YAML file containing extra parameters to put on end of url
        extra_params_lookup (str): Lookup key for parameters. If not given assumes parameters are at root of the dict.
        headers (Dict): Additional headers to add to request.
        status_forcelist (List[int]): HTTP statuses for which to force retry
        method_whitelist (iterable): HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).
    """

    def __init__(self, user_agent=None, user_agent_config_yaml=None, user_agent_lookup=None, use_env=True,
                 fail_on_missing_file=True, rate_limit=None, **kwargs):
        # type: (Optional[str], Optional[str], Optional[str], bool, bool, Optional[Dict], Any) -> None
        self.session = get_session(user_agent, user_agent_config_yaml, user_agent_lookup, use_env, fail_on_missing_file, **kwargs)
        self.response = None
        if rate_limit is not None:
            self.setup = sleep_and_retry(
                RateLimitDecorator(calls=rate_limit['calls'], period=rate_limit['period']).__call__(self.normal_setup))
        else:
            self.setup = self.normal_setup

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
        # type: () -> 'Download'
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Any, Any, Any) -> None
        self.close()

    @staticmethod
    def get_path_for_url(url, folder=None, filename=None, path=None, overwrite=False):
        # type: (str, Optional[str], Optional[str], Optional[str], bool) -> str
        """Get filename from url and join to provided folder or temporary folder if no folder supplied, ensuring uniqueness

        Args:
            url (str): URL to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            path (Optional[str]): Full path to use for downloaded file. Defaults to None (use folder and filename).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.

        Returns:
            str: Path of downloaded file

        """
        if path:
            if folder or filename:
                raise DownloadError('Cannot use folder or filename and path arguments together!')
            folder, filename = split(path)
        if not filename:
            urlpath = urlsplit(url).path
            filename = basename(urlpath)
        filename, extension = splitext(filename)
        if not folder:
            folder = get_temp_dir()
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

    @staticmethod
    def hxl_row(headers, hxltags, dict_form=False):
        # type: (List[str], Dict[str,str], bool) -> Union[List[str], Dict[str,str]]
        """Return HXL tag row for header row given list of headers and dictionary with header to HXL hashtag mappings.
        Return list or dictionary depending upon the dict_form argument.

        Args:
            headers (List[str]): Headers for which to get HXL hashtags
            hxltags (Dict[str,str]): Header to HXL hashtag mapping
            dict_form (bool): Return dict or list. Defaults to False (list)

        Returns:
            Union[List[str],Dict[str,str]]: Return either a list or dictionary conating HXL hashtags

        """
        if dict_form:
            return {header: hxltags.get(header, '') for header in headers}
        else:
            return [hxltags.get(header, '') for header in headers]

    def normal_setup(self, url, stream=True, post=False, parameters=None, timeout=None, headers=None, encoding=None):
        # type: (str, bool, bool, Optional[Dict], Optional[float], Optional[Dict], Optional[str]) -> requests.Response
        """Setup download from provided url returning the response

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
                    spliturl = spliturl._replace(scheme='http')
                    url = urlunsplit(spliturl)
            if post:
                full_url, parameters = self.get_url_params_for_post(url, parameters)
                self.response = self.session.post(full_url, data=parameters, stream=stream, timeout=timeout, headers=headers)
            else:
                self.response = self.session.get(self.get_url_for_get(url, parameters), stream=stream, timeout=timeout, headers=headers)
            self.response.raise_for_status()
            if encoding:
                self.response.encoding = encoding
        except Exception as e:
            raisefrom(DownloadError, 'Setup of Streaming Download of %s failed!' % url, e)
        return self.response

    def hash_stream(self, url):
        # type: (str) -> str
        """Stream file from url and hash it using MD5. Must call setup method first.

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
        except Exception as e:
            raisefrom(DownloadError, 'Download of %s failed in retrieval of stream!' % url, e)

    def stream_file(self, url, folder=None, filename=None, path=None, overwrite=False):
        # type: (str, Optional[str], Optional[str], Optional[str], bool) -> str
        """Stream file from url and store in provided folder or temporary folder if no folder supplied.
        Must call setup method first.

        Args:
            url (str): URL or path to download
            folder (Optional[str]): Folder to download it to. Defaults to None (temporary folder).
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            path (Optional[str]): Full path to use for downloaded file. Defaults to None (use folder and filename).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.

        Returns:
            str: Path of downloaded file

        """
        path = self.get_path_for_url(url, folder, filename, path, overwrite)
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

    def download_file(self, url, folder=None, filename=None, path=None, overwrite=False,
                      post=False, parameters=None, timeout=None, headers=None, encoding=None):
        # type: (str, Optional[str], Optional[str], Optional[str], bool, bool, Optional[Dict], Optional[float], Optional[Dict], Optional[str]) -> str
        """Download file from url and store in provided folder or temporary folder if no folder supplied

        Args:
            url (str): URL or path to download
            folder (Optional[str]): Folder to download it to. Defaults to None.
            filename (Optional[str]): Filename to use for downloaded file. Defaults to None (derive from the url).
            path (Optional[str]): Full path to use for downloaded file. Defaults to None (use folder and filename).
            overwrite (bool): Whether to overwrite existing file. Defaults to False.
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Optional[Dict]): Headers to pass. Defaults to None.
            encoding (Optional[str]): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            str: Path of downloaded file

        """
        self.setup(url, stream=True, post=post, parameters=parameters, timeout=timeout, headers=headers, encoding=encoding)
        return self.stream_file(url, folder, filename, path, overwrite)

    def download(self, url, post=False, parameters=None, timeout=None, headers=None, encoding=None):
        # type: (str, bool, Optional[Dict], Optional[float], Optional[Dict], Optional[str]) -> requests.Response
        """Download url

        Args:
            url (str): URL or path to download
            post (bool): Whether to use POST instead of GET. Defaults to False.
            parameters (Optional[Dict]): Parameters to pass. Defaults to None.
            timeout (Optional[float]): Timeout for connecting to URL. Defaults to None (no timeout).
            headers (Optional[Dict]): Headers to pass. Defaults to None.
            encoding (Optional[str]): Encoding to use for text response. Defaults to None (best guess).

        Returns:
            requests.Response: Response

        """
        return self.setup(url, stream=False, post=post, parameters=parameters, timeout=timeout, headers=headers, encoding=encoding)

    def get_yaml(self):
        # type: () -> Any
        """Get YAML content of download

        Returns:
            Any: YAML content of download

        """
        with YAML() as yaml:
            return yaml.load(self.response.text)

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
            url (str): URL or path to download
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
        if 'http_session' not in kwargs:
            kwargs['http_session'] = self.session
        try:
            self.response = tabulator.Stream(url, **kwargs)
            self.response.open()
            return self.response
        except Exception as e:
            raisefrom(DownloadError, 'Getting tabular stream for %s failed!' % url, e)

    def get_tabular_rows_as_list(self, url, **kwargs):
        # type: (str, Any) -> Iterator[List]
        """Get iterator for reading rows from tabular data. Each row is returned as a list.

        Args:
            url (str): URL or path to download
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Iterator[Union[List,Dict]]: Iterator where each row is returned as a list or dictionary.

        """
        return self.get_tabular_stream(url, **kwargs).iter(keyed=False)

    def get_tabular_rows(self, url, headers=1, dict_form=False, ignore_blank_rows=True, header_insertions=None, row_function=None, **kwargs):
        # type: (str, Union[int, List[int], List[str]], bool, bool, Optional[List[Tuple[int,str]]], Optional[Callable[[List[str],Union[List,Dict]],Union[List,Dict]]], Any) -> Tuple[List[str],Iterator[Union[List,Dict]]]
        """Returns header of tabular file pointed to by url and an iterator where each row is returned as a list
        or dictionary depending on the dict_rows argument. The headers argument is either a row number or list of row
        numbers (in case of multi-line headers) to be considered as headers (rows start counting at 1), or the actual
        headers defined as a list of strings. It defaults to 1 and cannot be None.  The dict_form arguments specifies
        if each row should be returned as a dictionary or a list, defaulting to a list.

        Optionally, headers can be inserted at specific positions. This is achieved using the header_insertions
        argument. If supplied, it is a list of tuples of the form (position, header) to be inserted. A function is
        called for each row. If supplied, it takes as arguments: headers (prior to any insertions) and
        row (which will be in dict or list form depending upon the dict_rows argument) and outputs a modified row
        or None to ignore the row.

        Args:
            url (str): URL or path to read from
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers. Defaults to 1.
            dict_form (bool): Return dict or list for each row. Defaults to False (list)
            ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
            header_insertions (Optional[List[Tuple[int,str]]]): List of (position, header) to insert. Defaults to None.
            row_function (Optional[Callable[[List[str],Union[List,Dict]],Union[List,Dict]]]): Function to call for each row. Defaults to None.
            **kwargs:
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Tuple[List[str],Iterator[Union[List,Dict]]]: Tuple (headers, iterator where each row is a list or dictionary)

        """
        if headers is None:
            raise DownloadError('Argument headers cannot be None!')
        if ignore_blank_rows:
            skip_rows = kwargs.get('skip_rows', list())
            if {'type': 'preset', 'value': 'blank'} not in skip_rows:
                skip_rows.append({'type': 'preset', 'value': 'blank'})
            kwargs['skip_rows'] = skip_rows
        stream = self.get_tabular_stream(url, headers=headers, **kwargs)
        origheaders = stream.headers
        if header_insertions is None or origheaders is None:
            headers = origheaders
        else:
            headers = copy.deepcopy(origheaders)
            for position, header in header_insertions:
                headers.insert(position, header)
        if row_function is None and ignore_blank_rows is False:
            return headers, stream.iter(keyed=dict_form)

        def get_next():
            for row in stream.iter(keyed=dict_form):
                if row_function:
                    processed_row = row_function(origheaders, row)
                    if processed_row is not None:
                        yield processed_row
                else:
                    yield row

        return headers, get_next()

    def download_tabular_key_value(self, url, **kwargs):
        # type: (str, Any) -> Dict
        """Download 2 column csv from url and return a dictionary of keys (first column) and values (second column)

        Args:
            url (str): URL or path to download
            **kwargs:
            headers (Union[int, List[int], List[str]]): Number of row(s) containing headers or list of headers
            file_type (Optional[str]): Type of file. Defaults to inferring.
            delimiter (Optional[str]): Delimiter used for values in each row. Defaults to inferring.

        Returns:
            Dict: Dictionary keys (first column) and values (second column)

        """
        output_dict = dict()
        for row in self.get_tabular_rows_as_list(url, **kwargs):
            if len(row) < 2:
                continue
            output_dict[row[0]] = row[1]
        return output_dict

    def download_tabular_rows_as_dicts(self, url, headers=1, keycolumn=1, **kwargs):
        # type: (str, Union[int, List[int], List[str]], int, Any) -> Dict[Dict]
        """Download multicolumn csv from url and return dictionary where keys are first column and values are
        dictionaries with keys from column headers and values from columns beneath

        Args:
            url (str): URL or path to download
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
            url (str): URL or path to download
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

    @staticmethod
    def get_column_positions(headers):
        # type: (List[str]) -> Dict[str,int]
        """Get mapping of headers to column positions

        Args:
            headers (List[str]): List of headers

        Returns:
            Dict[str,int]: Dictionary where keys are header names and values are header positions

        """
        columnpositions = dict()
        for i, header in enumerate(headers):
            columnpositions[header] = i
        return columnpositions
