<a id="hdx.utilities"></a>

# hdx.utilities

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/__init__.py#L1)

<a id="hdx.utilities.get_uuid"></a>

#### get\_uuid

```python
def get_uuid() -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/__init__.py#L6)

Get an UUID.

**Returns**:

- `str` - A UUID

<a id="hdx.utilities.is_valid_uuid"></a>

#### is\_valid\_uuid

```python
def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/__init__.py#L16)

Check if uuid_to_test is a valid UUID.

**Arguments**:

- `uuid_to_test` _str_ - UUID to test for validity
- `version` _int_ - UUID version. Defaults to 4.
  

**Returns**:

- `str` - Current script's directory

<a id="hdx.utilities.session"></a>

# hdx.utilities.session

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/session.py#L1)

Session utilities for urls

<a id="hdx.utilities.session.get_session"></a>

#### get\_session

```python
def get_session(user_agent: Optional[str] = None, user_agent_config_yaml: Optional[str] = None, user_agent_lookup: Optional[str] = None, use_env: bool = True, fail_on_missing_file: bool = True, **kwargs: Any, ,) -> requests.Session
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/session.py#L22)

Set up and return Session object that is set up with retrying. Requires either global user agent to be set or
appropriate user agent parameter(s) to be completed. If the EXTRA_PARAMS or BASIC_AUTH environment variable is
supplied, the extra_params* parameters will be ignored.

**Arguments**:

- `user_agent` _Optional[str]_ - User agent string. HDXPythonUtilities/X.X.X- is prefixed.
- `user_agent_config_yaml` _Optional[str]_ - Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
- `user_agent_lookup` _Optional[str]_ - Lookup key for YAML. Ignored if user_agent supplied.
- `use_env` _bool_ - Whether to read environment variables. Defaults to True.
- `fail_on_missing_file` _bool_ - Raise an exception if any specified configuration files are missing. Defaults to True.
- `**kwargs` - See below
- `auth` _Tuple[str, str]_ - Authorisation information in tuple form (user, pass) OR
- `basic_auth` _str_ - Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
- `basic_auth_file` _str_ - Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
- `extra_params_dict` _Dict_ - Extra parameters to put on end of url as a dictionary OR
- `extra_params_json` _str_ - Path to JSON file containing extra parameters to put on end of url OR
- `extra_params_yaml` _str_ - Path to YAML file containing extra parameters to put on end of url
- `extra_params_lookup` _str_ - Lookup key for parameters. If not given assumes parameters are at root of the dict.
- `headers` _Dict_ - Additional headers to add to request.
- `status_forcelist` _iterable_ - HTTP statuses for which to force retry. Defaults to [429, 500, 502, 503, 504].
- `allowed_methods` _iterable_ - HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).

<a id="hdx.utilities.wheel"></a>

# hdx.utilities.wheel

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/wheel.py#L1)

<a id="hdx.utilities.wheel.get_version_from_whl"></a>

#### get\_version\_from\_whl

```python
def get_version_from_whl(dirpath: str) -> Optional[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/wheel.py#L8)

Get version

**Arguments**:

- `dirpath` _str_ - Path where wheel resides
  

**Returns**:

- `Optional[str]` - Version if available or None

<a id="hdx.utilities.wheel.git_tag_whl"></a>

#### git\_tag\_whl

```python
def git_tag_whl(dirpath: str) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/wheel.py#L27)

Create git tag for whl given folder

**Arguments**:

- `dirpath` _str_ - Path where wheel resides
  

**Returns**:

  None

<a id="hdx.utilities.downloader"></a>

# hdx.utilities.downloader

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L1)

Downloading utilities for urls

<a id="hdx.utilities.downloader.Download"></a>

## Download Objects

```python
class Download()
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L27)

Download class with various download operations. Requires either global user agent to be set or appropriate
user agent parameter(s) to be completed.

**Arguments**:

- `user_agent` _Optional[str]_ - User agent string. HDXPythonUtilities/X.X.X- is prefixed.
- `user_agent_config_yaml` _Optional[str]_ - Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
- `user_agent_lookup` _Optional[str]_ - Lookup key for YAML. Ignored if user_agent supplied.
- `use_env` _bool_ - Whether to read environment variables. Defaults to True.
- `fail_on_missing_file` _bool_ - Raise an exception if any specified configuration files are missing. Defaults to True.
- `rate_limit` _Optional[Dict]_ - Rate limiting to use as a dict with calls and period. Defaults to None.
- `**kwargs` - See below
- `auth` _Tuple[str, str]_ - Authorisation information in tuple form (user, pass) OR
- `basic_auth` _str_ - Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
- `basic_auth_file` _str_ - Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
- `extra_params_dict` _Dict[str, str]_ - Extra parameters to put on end of url as a dictionary OR
- `extra_params_json` _str_ - Path to JSON file containing extra parameters to put on end of url OR
- `extra_params_yaml` _str_ - Path to YAML file containing extra parameters to put on end of url
- `extra_params_lookup` _str_ - Lookup key for parameters. If not given assumes parameters are at root of the dict.
- `headers` _Dict_ - Additional headers to add to request.
- `status_forcelist` _List[int]_ - HTTP statuses for which to force retry
- `allowed_methods` _iterable_ - HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).

<a id="hdx.utilities.downloader.Download.close_response"></a>

#### close\_response

```python
def close_response() -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L79)

Close response

**Returns**:

  None

<a id="hdx.utilities.downloader.Download.close"></a>

#### close

```python
def close() -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L92)

Close response and session

**Returns**:

  None

<a id="hdx.utilities.downloader.Download.get_path_for_url"></a>

#### get\_path\_for\_url

```python
@staticmethod
def get_path_for_url(url: str, folder: Optional[str] = None, filename: Optional[str] = None, path: Optional[str] = None, overwrite: bool = False) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L109)

Get filename from url and join to provided folder or temporary folder if no folder supplied, ensuring uniqueness

**Arguments**:

- `url` _str_ - URL to download
- `folder` _Optional[str]_ - Folder to download it to. Defaults to None (temporary folder).
- `filename` _Optional[str]_ - Filename to use for downloaded file. Defaults to None (derive from the url).
- `path` _Optional[str]_ - Full path to use for downloaded file. Defaults to None (use folder and filename).
- `overwrite` _bool_ - Whether to overwrite existing file. Defaults to False.
  

**Returns**:

- `str` - Path of downloaded file

<a id="hdx.utilities.downloader.Download.get_full_url"></a>

#### get\_full\_url

```python
def get_full_url(url: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L153)

Get full url including any additional parameters

**Arguments**:

- `url` _str_ - URL for which to get full url
  

**Returns**:

- `str` - Full url including any additional parameters

<a id="hdx.utilities.downloader.Download.get_url_for_get"></a>

#### get\_url\_for\_get

```python
@staticmethod
def get_url_for_get(url: str, parameters: Optional[Dict] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L167)

Get full url for GET request including parameters

**Arguments**:

- `url` _str_ - URL to download
- `parameters` _Optional[Dict]_ - Parameters to pass. Defaults to None.
  

**Returns**:

- `str` - Full url

<a id="hdx.utilities.downloader.Download.get_url_params_for_post"></a>

#### get\_url\_params\_for\_post

```python
@staticmethod
def get_url_params_for_post(url: str, parameters: Optional[Dict] = None) -> Tuple[str, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L186)

Get full url for POST request and all parameters including any in the url

**Arguments**:

- `url` _str_ - URL to download
- `parameters` _Optional[Dict]_ - Parameters to pass. Defaults to None.
  

**Returns**:

  Tuple[str, Dict]: (Full url, parameters)

<a id="hdx.utilities.downloader.Download.hxl_row"></a>

#### hxl\_row

```python
@staticmethod
def hxl_row(headers: List[str], hxltags: Dict[str, str], dict_form: bool = False) -> Union[List[str], Dict[str, str]]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L208)

Return HXL tag row for header row given list of headers and dictionary with header to HXL hashtag mappings.
Return list or dictionary depending upon the dict_form argument.

**Arguments**:

- `headers` _List[str]_ - Headers for which to get HXL hashtags
- `hxltags` _Dict[str,str]_ - Header to HXL hashtag mapping
- `dict_form` _bool_ - Return dict or list. Defaults to False (list)
  

**Returns**:

- `Union[List[str],Dict[str,str]]` - Return either a list or dictionary conating HXL hashtags

<a id="hdx.utilities.downloader.Download.normal_setup"></a>

#### normal\_setup

```python
def normal_setup(url: str, stream: bool = True, post: bool = False, parameters: Optional[Dict] = None, timeout: Optional[float] = None, headers: Optional[Dict] = None, encoding: Optional[str] = None) -> requests.Response
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L228)

Setup download from provided url returning the response

**Arguments**:

- `url` _str_ - URL or path to download
- `stream` _bool_ - Whether to stream download. Defaults to True.
- `post` _bool_ - Whether to use POST instead of GET. Defaults to False.
- `parameters` _Optional[Dict]_ - Parameters to pass. Defaults to None.
- `timeout` _Optional[float]_ - Timeout for connecting to URL. Defaults to None (no timeout).
- `headers` _Optional[Dict]_ - Headers to pass. Defaults to None.
- `encoding` _Optional[str]_ - Encoding to use for text response. Defaults to None (best guess).
  

**Returns**:

- `requests.Response` - requests.Response object

<a id="hdx.utilities.downloader.Download.hash_stream"></a>

#### hash\_stream

```python
def hash_stream(url: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L290)

Stream file from url and hash it using MD5. Must call setup method first.

**Arguments**:

- `url` _str_ - URL or path to download
  

**Returns**:

- `str` - MD5 hash of file

<a id="hdx.utilities.downloader.Download.stream_file"></a>

#### stream\_file

```python
def stream_file(url: str, folder: Optional[str] = None, filename: Optional[str] = None, path: Optional[str] = None, overwrite: bool = False) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L311)

Stream file from url and store in provided folder or temporary folder if no folder supplied.
Must call setup method first.

**Arguments**:

- `url` _str_ - URL or path to download
- `folder` _Optional[str]_ - Folder to download it to. Defaults to None (temporary folder).
- `filename` _Optional[str]_ - Filename to use for downloaded file. Defaults to None (derive from the url).
- `path` _Optional[str]_ - Full path to use for downloaded file. Defaults to None (use folder and filename).
- `overwrite` _bool_ - Whether to overwrite existing file. Defaults to False.
  

**Returns**:

- `str` - Path of downloaded file

<a id="hdx.utilities.downloader.Download.download_file"></a>

#### download\_file

```python
def download_file(url: str, folder: Optional[str] = None, filename: Optional[str] = None, path: Optional[str] = None, overwrite: bool = False, post: bool = False, parameters: Optional[Dict] = None, timeout: Optional[float] = None, headers: Optional[Dict] = None, encoding: Optional[str] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L350)

Download file from url and store in provided folder or temporary folder if no folder supplied

**Arguments**:

- `url` _str_ - URL or path to download
- `folder` _Optional[str]_ - Folder to download it to. Defaults to None.
- `filename` _Optional[str]_ - Filename to use for downloaded file. Defaults to None (derive from the url).
- `path` _Optional[str]_ - Full path to use for downloaded file. Defaults to None (use folder and filename).
- `overwrite` _bool_ - Whether to overwrite existing file. Defaults to False.
- `post` _bool_ - Whether to use POST instead of GET. Defaults to False.
- `parameters` _Optional[Dict]_ - Parameters to pass. Defaults to None.
- `timeout` _Optional[float]_ - Timeout for connecting to URL. Defaults to None (no timeout).
- `headers` _Optional[Dict]_ - Headers to pass. Defaults to None.
- `encoding` _Optional[str]_ - Encoding to use for text response. Defaults to None (best guess).
  

**Returns**:

- `str` - Path of downloaded file

<a id="hdx.utilities.downloader.Download.download"></a>

#### download

```python
def download(url: str, post: bool = False, parameters: Optional[Dict] = None, timeout: Optional[float] = None, headers: Optional[Dict] = None, encoding: Optional[str] = None) -> requests.Response
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L392)

Download url

**Arguments**:

- `url` _str_ - URL or path to download
- `post` _bool_ - Whether to use POST instead of GET. Defaults to False.
- `parameters` _Optional[Dict]_ - Parameters to pass. Defaults to None.
- `timeout` _Optional[float]_ - Timeout for connecting to URL. Defaults to None (no timeout).
- `headers` _Optional[Dict]_ - Headers to pass. Defaults to None.
- `encoding` _Optional[str]_ - Encoding to use for text response. Defaults to None (best guess).
  

**Returns**:

- `requests.Response` - Response

<a id="hdx.utilities.downloader.Download.get_header"></a>

#### get\_header

```python
def get_header(header: str) -> Any
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L425)

Get a particular response header of download

**Arguments**:

- `header` _str_ - Header for which to get value
  

**Returns**:

- `Any` - Response header's value

<a id="hdx.utilities.downloader.Download.get_headers"></a>

#### get\_headers

```python
def get_headers() -> Any
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L437)

Get response headers of download

**Returns**:

- `Any` - Response headers

<a id="hdx.utilities.downloader.Download.get_status"></a>

#### get\_status

```python
def get_status() -> int
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L446)

Get response status code

**Returns**:

- `int` - Response status code

<a id="hdx.utilities.downloader.Download.get_text"></a>

#### get\_text

```python
def get_text() -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L455)

Get text content of download

**Returns**:

- `str` - Text content of download

<a id="hdx.utilities.downloader.Download.get_yaml"></a>

#### get\_yaml

```python
def get_yaml() -> Any
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L464)

Get YAML content of download

**Returns**:

- `Any` - YAML content of download

<a id="hdx.utilities.downloader.Download.get_json"></a>

#### get\_json

```python
def get_json() -> Any
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L474)

Get JSON content of download

**Returns**:

- `Any` - JSON content of download

<a id="hdx.utilities.downloader.Download.get_tabular_stream"></a>

#### get\_tabular\_stream

```python
def get_tabular_stream(url: str, **kwargs: Any) -> tabulator.Stream
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L483)

Get Tabulator stream.

**Arguments**:

- `url` _str_ - URL or path to download
  **kwargs:
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `tabulator.Stream` - Tabulator Stream object

<a id="hdx.utilities.downloader.Download.get_tabular_rows_as_list"></a>

#### get\_tabular\_rows\_as\_list

```python
def get_tabular_rows_as_list(url: str, **kwargs: Any) -> Iterator[List]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L513)

Get iterator for reading rows from tabular data. Each row is returned as a list.

**Arguments**:

- `url` _str_ - URL or path to download
  **kwargs:
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `Iterator[Union[List,Dict]]` - Iterator where each row is returned as a list or dictionary.

<a id="hdx.utilities.downloader.Download.get_tabular_rows"></a>

#### get\_tabular\_rows

```python
def get_tabular_rows(url: str, headers: Union[int, List[int], List[str]] = 1, dict_form: bool = False, ignore_blank_rows: bool = True, header_insertions: Optional[List[Tuple[int, str]]] = None, row_function: Optional[
            Callable[[List[str], Union[List, Dict]], Union[List, Dict]]
        ] = None, **kwargs: Any, ,) -> Tuple[List[str], Iterator[Union[List, Dict]]]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L531)

Returns header of tabular file pointed to by url and an iterator where each row is returned as a list
or dictionary depending on the dict_rows argument. The headers argument is either a row number or list of row
numbers (in case of multi-line headers) to be considered as headers (rows start counting at 1), or the actual
headers defined as a list of strings. It defaults to 1 and cannot be None.  The dict_form arguments specifies
if each row should be returned as a dictionary or a list, defaulting to a list.

Optionally, headers can be inserted at specific positions. This is achieved using the header_insertions
argument. If supplied, it is a list of tuples of the form (position, header) to be inserted. A function is
called for each row. If supplied, it takes as arguments: headers (prior to any insertions) and
row (which will be in dict or list form depending upon the dict_rows argument) and outputs a modified row
or None to ignore the row.

**Arguments**:

- `url` _str_ - URL or path to read from
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers. Defaults to 1.
- `dict_form` _bool_ - Return dict or list for each row. Defaults to False (list)
- `ignore_blank_rows` _bool_ - Whether to ignore blank rows. Defaults to True.
- `header_insertions` _Optional[List[Tuple[int,str]]]_ - List of (position, header) to insert. Defaults to None.
- `row_function` _Optional[Callable[[List[str],Union[List,Dict]],Union[List,Dict]]]_ - Function to call for each row. Defaults to None.
  **kwargs:
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `Tuple[List[str],Iterator[Union[List,Dict]]]` - Tuple (headers, iterator where each row is a list or dictionary)

<a id="hdx.utilities.downloader.Download.download_tabular_key_value"></a>

#### download\_tabular\_key\_value

```python
def download_tabular_key_value(url: str, **kwargs: Any) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L599)

Download 2 column csv from url and return a dictionary of keys (first column) and values (second column)

**Arguments**:

- `url` _str_ - URL or path to download
  **kwargs:
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `Dict` - Dictionary keys (first column) and values (second column)

<a id="hdx.utilities.downloader.Download.download_tabular_rows_as_dicts"></a>

#### download\_tabular\_rows\_as\_dicts

```python
def download_tabular_rows_as_dicts(url: str, headers: Union[int, List[int], List[str]] = 1, keycolumn: int = 1, **kwargs: Any, ,) -> Dict[str, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L620)

Download multicolumn csv from url and return dictionary where keys are first column and values are
dictionaries with keys from column headers and values from columns beneath

**Arguments**:

- `url` _str_ - URL or path to download
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers. Defaults to 1.
- `keycolumn` _int_ - Number of column to be used for key. Defaults to 1.
  **kwargs:
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `Dict[str,Dict]` - Dictionary where keys are first column and values are dictionaries with keys from column
  headers and values from columns beneath

<a id="hdx.utilities.downloader.Download.download_tabular_cols_as_dicts"></a>

#### download\_tabular\_cols\_as\_dicts

```python
def download_tabular_cols_as_dicts(url: str, headers: Union[int, List[int], List[str]] = 1, keycolumn: int = 1, **kwargs: Any, ,) -> Dict[str, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L658)

Download multicolumn csv from url and return dictionary where keys are header names and values are
dictionaries with keys from first column and values from other columns

**Arguments**:

- `url` _str_ - URL or path to download
- `headers` _Union[int, List[int], List[str]]_ - Number of row(s) containing headers or list of headers. Defaults to 1.
- `keycolumn` _int_ - Number of column to be used for key. Defaults to 1.
  **kwargs:
- `file_type` _Optional[str]_ - Type of file. Defaults to inferring.
- `delimiter` _Optional[str]_ - Delimiter used for values in each row. Defaults to inferring.
  

**Returns**:

- `Dict[str,Dict]` - Dictionary where keys are header names and values are dictionaries with keys from first column
  and values from other columns

<a id="hdx.utilities.downloader.Download.get_column_positions"></a>

#### get\_column\_positions

```python
@staticmethod
def get_column_positions(headers: List[str]) -> Dict[str, int]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/downloader.py#L698)

Get mapping of headers to column positions

**Arguments**:

- `headers` _List[str]_ - List of headers
  

**Returns**:

- `Dict[str,int]` - Dictionary where keys are header names and values are header positions

<a id="hdx.utilities.loader"></a>

# hdx.utilities.loader

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L1)

Loading utilities for YAML, JSON etc.

<a id="hdx.utilities.loader.load_file_to_str"></a>

#### load\_file\_to\_str

```python
def load_file_to_str(path: str, encoding: str = "utf-8", strip: bool = False, replace_newlines: Optional[str] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L19)

Load file into a string removing newlines

**Arguments**:

- `path` _str_ - Path to file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
- `strip` _bool_ - Whether to strip whitespace from start and end. Defaults to False.
- `replace_newlines` _Optional[str]_ - String with which tp replace newlines. Defaults to None (don't replace).
  

**Returns**:

- `str` - String contents of file

<a id="hdx.utilities.loader.load_yaml"></a>

#### load\_yaml

```python
def load_yaml(path: str, encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L49)

Load YAML file into an ordered dictionary

**Arguments**:

- `path` _str_ - Path to YAML file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `Dict` - Ordered dictionary containing loaded YAML file

<a id="hdx.utilities.loader.load_json"></a>

#### load\_json

```python
def load_json(path: str, encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L67)

Load JSON file into an ordered dictionary (dict for Python 3.7+)

**Arguments**:

- `path` _str_ - Path to JSON file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `Dict` - Ordered dictionary containing loaded JSON file

<a id="hdx.utilities.loader.load_and_merge_yaml"></a>

#### load\_and\_merge\_yaml

```python
def load_and_merge_yaml(paths: List[str], encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L84)

Load multiple YAML files and merge into one dictionary

**Arguments**:

- `paths` _List[str]_ - Paths to YAML files
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `Dict` - Dictionary of merged YAML files

<a id="hdx.utilities.loader.load_and_merge_json"></a>

#### load\_and\_merge\_json

```python
def load_and_merge_json(paths: List[str], encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L99)

Load multiple JSON files and merge into one dictionary

**Arguments**:

- `paths` _List[str]_ - Paths to JSON files
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `Dict` - Dictionary of merged JSON files

<a id="hdx.utilities.loader.load_yaml_into_existing_dict"></a>

#### load\_yaml\_into\_existing\_dict

```python
def load_yaml_into_existing_dict(data: dict, path: str, encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L114)

Merge YAML file into existing dictionary

**Arguments**:

- `data` _dict_ - Dictionary to merge into
- `path` _str_ - YAML file to load and merge
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `Dict` - YAML file merged into dictionary

<a id="hdx.utilities.loader.load_json_into_existing_dict"></a>

#### load\_json\_into\_existing\_dict

```python
def load_json_into_existing_dict(data: dict, path: str, encoding: str = "utf-8") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/loader.py#L131)

Merge JSON file into existing dictionary

**Arguments**:

- `data` _dict_ - Dictionary to merge into
- `path` _str_ - JSON file to load and merge
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

- `dict` - JSON file merged into dictionary

<a id="hdx.utilities.retriever"></a>

# hdx.utilities.retriever

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L1)

<a id="hdx.utilities.retriever.Retrieve"></a>

## Retrieve Objects

```python
class Retrieve()
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L13)

Retrieve class which takes in a Download object and can either download, download and save or use previously
downloaded and saved data. It also allows the use of a static fallback when downloading fails.

**Arguments**:

- `downloader` _Download_ - Download object
- `fallback_dir` _str_ - Directory containing static fallback data
- `saved_dir` _str_ - Directory to save or load downloaded data
- `temp_dir` _str_ - Temporary directory for when data is not needed after downloading
- `save` _bool_ - Whether to save downloaded data. Defaults to False.
- `use_saved` _bool_ - Whether to use saved data. Defaults to False.

<a id="hdx.utilities.retriever.Retrieve.get_url_logstr"></a>

#### get\_url\_logstr

```python
@staticmethod
def get_url_logstr(url: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L50)

Url string that will be logged. It is limited to 100 characters if necessary.

**Arguments**:

- `url` _str_ - URL to download
  

**Returns**:

- `str` - Url string to use in logs

<a id="hdx.utilities.retriever.Retrieve.retrieve_file"></a>

#### retrieve\_file

```python
def retrieve_file(url, filename, logstr=None, fallback=False, **kwargs)
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L64)

Retrieve file

**Arguments**:

- `url` _str_ - URL to download
- `filename` _str_ - Filename to use for saved file
- `logstr` _Optional[str]_ - Text to use in log string to describe download. Defaults to filename.
- `fallback` _bool_ - Whether to use static fallback if download fails. Defaults to False.
- `**kwargs` - Parameters to pass to download_file call
  

**Returns**:

- `str` - Path to downloaded file

<a id="hdx.utilities.retriever.Retrieve.retrieve_text"></a>

#### retrieve\_text

```python
def retrieve_text(url, filename, logstr=None, fallback=False, **kwargs)
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L108)

Retrieve text

**Arguments**:

- `url` _str_ - URL to download
- `filename` _str_ - Filename to use for saved file
- `logstr` _Optional[str]_ - Text to use in log string to describe download. Defaults to filename.
- `fallback` _bool_ - Whether to use static fallback if download fails. Defaults to False.
- `**kwargs` - Parameters to pass to download call
  

**Returns**:

- `Union[Dict,List]` - The text from the file

<a id="hdx.utilities.retriever.Retrieve.retrieve_yaml"></a>

#### retrieve\_yaml

```python
def retrieve_yaml(url, filename, logstr=None, fallback=False, **kwargs)
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L150)

Retrieve YAML

**Arguments**:

- `url` _str_ - URL to download
- `filename` _str_ - Filename to use for saved file
- `logstr` _Optional[str]_ - Text to use in log string to describe download. Defaults to filename.
- `fallback` _bool_ - Whether to use static fallback if download fails. Defaults to False.
- `**kwargs` - Parameters to pass to download call
  

**Returns**:

- `Union[Dict,List]` - The data from the YAML file

<a id="hdx.utilities.retriever.Retrieve.retrieve_json"></a>

#### retrieve\_json

```python
def retrieve_json(url, filename, logstr=None, fallback=False, **kwargs)
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/retriever.py#L192)

Retrieve JSON

**Arguments**:

- `url` _str_ - URL to download
- `filename` _str_ - Filename to use for saved file
- `logstr` _Optional[str]_ - Text to use in log string to describe download. Defaults to filename.
- `fallback` _bool_ - Whether to use static fallback if download fails. Defaults to False.
- `**kwargs` - Parameters to pass to download call
  

**Returns**:

- `Union[Dict,List]` - The data from the JSON file

<a id="hdx.utilities.text"></a>

# hdx.utilities.text

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L1)

Text processing utilities

<a id="hdx.utilities.text.remove_end_characters"></a>

#### remove\_end\_characters

```python
def remove_end_characters(string: str, characters_to_remove: str = punctuation) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L14)

Remove any characters at end of string that are in characters_to_remove

**Arguments**:

- `string` _str_ - Input string
- `characters_to_remove` _str_ - Characters to remove. Defaults to punctuation.
  

**Returns**:

- `str` - String with any characters at end of string that are in characters_to_remove removed

<a id="hdx.utilities.text.remove_from_end"></a>

#### remove\_from\_end

```python
def remove_from_end(string: str, things_to_remove: List[str], logging_text: Optional[str] = None, whole_words: bool = True) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L32)

Remove list of items from end of string, stripping any whitespace

**Arguments**:

- `string` _str_ - Input string
- `things_to_remove` _List[str]_ - Things to remove from the end of string
- `logging_text` _Optional[str]_ - Text to log. Defaults to None.
- `whole_words` _bool_ - Remove parts of or whole words. Defaults to True (whole words only).
  

**Returns**:

- `str` - String with text removed

<a id="hdx.utilities.text.remove_string"></a>

#### remove\_string

```python
def remove_string(string: str, toremove: str, end_characters_to_remove: str = punctuation) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L67)

Remove string from another string and delete any preceding end characters - by default punctuation (eg. comma)
and any whitespace following the punctuation

**Arguments**:

- `string` _str_ - String to process
- `toremove` _str_ - String to remove
- `end_characters_to_remove` _str_ - Characters to remove. Defaults to punctuation.
  

**Returns**:

- `str` - String with other string removed

<a id="hdx.utilities.text.multiple_replace"></a>

#### multiple\_replace

```python
def multiple_replace(string: str, replacements: Dict[str, str]) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L91)

Simultaneously replace multiple strings in a string

**Arguments**:

- `string` _str_ - Input string
- `replacements` _Dict[str,str]_ - Replacements dictionary
  

**Returns**:

- `str` - String with replacements

<a id="hdx.utilities.text.get_words_in_sentence"></a>

#### get\_words\_in\_sentence

```python
def get_words_in_sentence(sentence: str) -> List[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L113)

Returns list of words in a sentence

**Arguments**:

- `sentence` _str_ - Sentence
  

**Returns**:

- `List[str]` - List of words in sentence

<a id="hdx.utilities.text.get_matching_text_in_strs"></a>

#### get\_matching\_text\_in\_strs

```python
def get_matching_text_in_strs(a: str, b: str, match_min_size: int = 30, ignore: str = "", end_characters: str = "") -> List[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L128)

Returns a list of matching blocks of text in a and b

**Arguments**:

- `a` _str_ - First string to match
- `b` _str_ - Second string to match
- `match_min_size` _int_ - Minimum block size to match on. Defaults to 30.
- `ignore` _str_ - Any characters to ignore in matching. Defaults to ''.
- `end_characters` _str_ - End characters to look for. Defaults to ''.
  

**Returns**:

- `List[str]` - List of matching blocks of text

<a id="hdx.utilities.text.get_matching_text"></a>

#### get\_matching\_text

```python
def get_matching_text(string_list: List[str], match_min_size: int = 30, ignore: str = "", end_characters: str = ".!\r\n") -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L168)

Returns a string containing matching blocks of text in a list of strings followed by non-matching.

**Arguments**:

- `string_list` _List[str]_ - List of strings to match
- `match_min_size` _int_ - Minimum block size to match on. Defaults to 30.
- `ignore` _str_ - Any characters to ignore in matching. Defaults to ''.
- `end_characters` _str_ - End characters to look for. Defaults to '.\r\n'.
  

**Returns**:

- `str` - String containing matching blocks of text followed by non-matching

<a id="hdx.utilities.text.get_matching_then_nonmatching_text"></a>

#### get\_matching\_then\_nonmatching\_text

```python
def get_matching_then_nonmatching_text(string_list: List[str], separator: str = "", match_min_size: int = 30, ignore: str = "", end_characters: str = ".!\r\n") -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L200)

Returns a string containing matching blocks of text in a list of strings followed by non-matching.

**Arguments**:

- `string_list` _List[str]_ - List of strings to match
- `separator` _str_ - Separator to add between blocks of text. Defaults to ''.
- `match_min_size` _int_ - Minimum block size to match on. Defaults to 30.
- `ignore` _str_ - Any characters to ignore in matching. Defaults to ''.
- `end_characters` _str_ - End characters to look for. Defaults to '.\r\n'.
  

**Returns**:

- `str` - String containing matching blocks of text followed by non-matching

<a id="hdx.utilities.text.number_format"></a>

#### number\_format

```python
def number_format(val: Any, format: str = "%.4f", trailing_zeros: bool = True) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L288)

Format float-castable input as string

**Arguments**:

- `val` _float_ - Number to format
- `format` _str_ - Format to use. Defaults to %.4f.
- `trailing_zeros` _bool_ - Leave trailing zeros. Defaults to True.
  

**Returns**:

- `str` - Formatted number as string

<a id="hdx.utilities.text.get_fraction_str"></a>

#### get\_fraction\_str

```python
def get_fraction_str(numerator: Any, denominator: Optional[Any] = None, format: str = "%.4f", trailing_zeros: bool = True) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L309)

Given float-castable numerator and optional float-castable denominator, format as string, returning '' for
invalid numerator or 0 denominator.

**Arguments**:

- `numerator` _float_ - Numerator
- `denominator` _Optional[float]_ - Denominator. Defaults to None.
- `format` _str_ - Format to use. Defaults to %.4f.
- `trailing_zeros` _bool_ - Leave trailing zeros. Defaults to True.
  

**Returns**:

- `str` - Formatted number as string

<a id="hdx.utilities.text.only_allowed_in_str"></a>

#### only\_allowed\_in\_str

```python
def only_allowed_in_str(test_str: str, allowed_chars: Set) -> bool
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L340)

Returns True if test string contains only allowed characters, False if not.

**Arguments**:

- `test_str` _str_ - Test string
- `allowed_chars` _Set_ - Set of allowed characters
  

**Returns**:

- `bool` - True if test string contains only allowed characters, False if not

<a id="hdx.utilities.text.get_numeric_if_possible"></a>

#### get\_numeric\_if\_possible

```python
def get_numeric_if_possible(value: Any) -> Any
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/text.py#L356)

Return val if it is not a string, otherwise see if it can be cast to float or int,
taking into account commas and periods.

**Arguments**:

- `value` _Any_ - Value
  

**Returns**:

- `Any` - Value

<a id="hdx.utilities.useragent"></a>

# hdx.utilities.useragent

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/useragent.py#L1)

User agent utilities

<a id="hdx.utilities.useragent.UserAgent"></a>

## UserAgent Objects

```python
class UserAgent()
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/useragent.py#L17)

<a id="hdx.utilities.useragent.UserAgent.clear_global"></a>

#### clear\_global

```python
@classmethod
def clear_global(cls) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/useragent.py#L149)

Clear stored user agent string

**Returns**:

  None

<a id="hdx.utilities.useragent.UserAgent.set_global"></a>

#### set\_global

```python
@classmethod
def set_global(cls, user_agent: Optional[str] = None, user_agent_config_yaml: Optional[str] = None, user_agent_lookup: Optional[str] = None, **kwargs: Any, ,) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/useragent.py#L160)

Set global user agent string

**Arguments**:

- `user_agent` _Optional[str]_ - User agent string. HDXPythonLibrary/X.X.X- is prefixed.
- `user_agent_config_yaml` _Optional[str]_ - Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
- `user_agent_lookup` _Optional[str]_ - Lookup key for YAML. Ignored if user_agent supplied.
  

**Returns**:

  None

<a id="hdx.utilities.useragent.UserAgent.get"></a>

#### get

```python
@classmethod
def get(cls, user_agent: Optional[str] = None, user_agent_config_yaml: Optional[str] = None, user_agent_lookup: Optional[str] = None, **kwargs: Any, ,) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/useragent.py#L183)

Get full user agent string from parameters if supplied falling back on global user agent if set.

**Arguments**:

- `user_agent` _Optional[str]_ - User agent string. HDXPythonLibrary/X.X.X- is prefixed.
- `user_agent_config_yaml` _Optional[str]_ - Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
- `user_agent_lookup` _Optional[str]_ - Lookup key for YAML. Ignored if user_agent supplied.
  

**Returns**:

- `str` - Full user agent string

<a id="hdx.utilities.saver"></a>

# hdx.utilities.saver

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/saver.py#L1)

Saving utilities for YAML, JSON etc.

<a id="hdx.utilities.saver.save_str_to_file"></a>

#### save\_str\_to\_file

```python
def save_str_to_file(string: str, path: str, encoding: str = "utf-8") -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/saver.py#L52)

Save string to file

**Arguments**:

- `string` _str_ - String to save
- `path` _str_ - Path to file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
  

**Returns**:

  None

<a id="hdx.utilities.saver.save_yaml"></a>

#### save\_yaml

```python
def save_yaml(dictionary: Dict, path: str, encoding: str = "utf-8", pretty: bool = False, sortkeys: bool = False) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/saver.py#L67)

Save dictionary to YAML file preserving order if it is an OrderedDict

**Arguments**:

- `dictionary` _Dict_ - Python dictionary to save
- `path` _str_ - Path to YAML file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
- `pretty` _bool_ - Whether to pretty print. Defaults to False.
- `sortkeys` _bool_ - Whether to sort dictionary keys. Defaults to False.
  

**Returns**:

  None

<a id="hdx.utilities.saver.save_json"></a>

#### save\_json

```python
def save_json(dictionary: Dict, path: str, encoding: str = "utf-8", pretty: bool = False, sortkeys: bool = False) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/saver.py#L103)

Save dictionary to JSON file preserving order if it is an OrderedDict

**Arguments**:

- `dictionary` _Dict_ - Python dictionary to save
- `path` _str_ - Path to JSON file
- `encoding` _str_ - Encoding of file. Defaults to utf-8.
- `pretty` _bool_ - Whether to pretty print. Defaults to False.
- `sortkeys` _bool_ - Whether to sort dictionary keys. Defaults to False.
  

**Returns**:

  None

<a id="hdx.utilities.path"></a>

# hdx.utilities.path

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L1)

Directory Path Utilities

<a id="hdx.utilities.path.script_dir"></a>

#### script\_dir

```python
def script_dir(pyobject: Any, follow_symlinks: bool = True) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L25)

Get current script's directory

**Arguments**:

- `pyobject` _Any_ - Any Python object in the script
- `follow_symlinks` _bool_ - Follow symlinks or not. Defaults to True.
  

**Returns**:

- `str` - Current script's directory

<a id="hdx.utilities.path.script_dir_plus_file"></a>

#### script\_dir\_plus\_file

```python
def script_dir_plus_file(filename: str, pyobject: Any, follow_symlinks: bool = True) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L44)

Get current script's directory and then append a filename

**Arguments**:

- `filename` _str_ - Filename to append to directory path
- `pyobject` _Any_ - Any Python object in the script
- `follow_symlinks` _bool_ - Follow symlinks or not. Defaults to True.
  

**Returns**:

- `str` - Current script's directory and with filename appended

<a id="hdx.utilities.path.get_temp_dir"></a>

#### get\_temp\_dir

```python
def get_temp_dir(folder: Optional[str] = None, delete_if_exists: bool = False, tempdir: Optional[str] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L60)

Get a temporary directory. Looks for environment variable TEMP_DIR and falls
back on os.gettempdir if a root temporary directory is not supplied. If a folder is supplied, creates that folder
within the temporary directory. Optionally deletes and recreates it if it already exists.

**Arguments**:

- `folder` _Optional[str]_ - Folder to create in temporary folder. Defaults to None.
- `delete_if_exists` _bool_ - Whether to delete the folder if it exists. Defaults to False.
- `tempdir` _Optional[str]_ - Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).
  

**Returns**:

- `str` - A temporary directory

<a id="hdx.utilities.path.temp_dir"></a>

#### temp\_dir

```python
@contextlib.contextmanager
def temp_dir(folder: Optional[str] = None, delete_if_exists: bool = False, delete_on_success: bool = True, delete_on_failure: bool = True, tempdir: Optional[str] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L91)

Get a temporary directory optionally with folder appended (and created if it doesn't exist)

**Arguments**:

- `folder` _Optional[str]_ - Folder to create in temporary folder. Defaults to None.
- `delete_if_exists` _bool_ - Whether to delete the folder if it exists. Defaults to False.
- `delete_on_success` _bool_ - Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
- `delete_on_failure` _bool_ - Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
- `tempdir` _Optional[str]_ - Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).
  

**Returns**:

- `str` - A temporary directory

<a id="hdx.utilities.path.read_or_create_batch"></a>

#### read\_or\_create\_batch

```python
def read_or_create_batch(folder: str, batch: Optional[str] = None) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L124)

Get batch or create it if it doesn't exist

**Arguments**:

- `folder` _str_ - Folder in which to look for or create batch file.
- `batch` _Optional[str]_ - Batch to use if there isn't one in a file already.
  

**Returns**:

- `str` - Batch

<a id="hdx.utilities.path.temp_dir_batch"></a>

#### temp\_dir\_batch

```python
@contextlib.contextmanager
def temp_dir_batch(folder: Optional[str] = None, delete_if_exists: bool = False, delete_on_success: bool = True, delete_on_failure: bool = True, batch: Optional[str] = None, tempdir: Optional[str] = None) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L147)

Get a temporary directory and batch id. Yields a dictionary with key folder which is the temporary directory
optionally with folder appended (and created if it doesn't exist). In key batch is a batch code to be passed as
the batch parameter in create_in_hdx or update_in_hdx calls.

**Arguments**:

- `folder` _Optional[str]_ - Folder to create in temporary folder. Defaults to None.
- `delete_if_exists` _bool_ - Whether to delete the folder if it exists. Defaults to False.
- `delete_on_success` _bool_ - Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
- `delete_on_failure` _bool_ - Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
- `batch` _Optional[str]_ - Batch to use if there isn't one in a file already.
- `tempdir` _Optional[str]_ - Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).
  

**Returns**:

- `Dict` - Dictionary containing temporary directory in key folder and batch id in key batch

<a id="hdx.utilities.path.get_wheretostart"></a>

#### get\_wheretostart

```python
def get_wheretostart(text: str, message: str, key: str) -> Optional[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L183)

Evaluate WHERETOSTART.

**Arguments**:

- `text` _str_ - String to process
- `message` _str_ - Text for logging
- `key` _str_ - Key to comapre with
  

**Returns**:

- `Optional[str]` - A string or None

<a id="hdx.utilities.path.progress_storing_folder"></a>

#### progress\_storing\_folder

```python
def progress_storing_folder(info: Dict, iterator: Iterable[Dict], key: str, wheretostart: Optional[str] = None) -> Tuple[Dict, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L205)

Store progress in folder in key folder of info dictionary parameter. Yields 2 dictionaries. The first is the
info dictionary. It contains in key folder the folder being used to store progress and in key progress the current
position in the iterator. If store_batch is True, that dictionary will also contain the key batch containing a batch
code to be passed as the batch parameter in create_in_hdx or update_in_hdx calls. The second dictionary is the next
dictionary in the iterator.

**Arguments**:

- `info` _Dict_ - Dictionary containing folder and anything else to be yielded
- `iterator` _Iterable[Dict]_ - Iterate over this object persisting progress
- `key` _str_ - Key to examine from dictionary from iterator
- `wheretostart` _Optional[str]_ - Where in iterator to start
  

**Returns**:

- `Tuple[Dict,Dict]` - A tuple of the form (info dictionary, next object in iterator)

<a id="hdx.utilities.path.wheretostart_tempdir_batch"></a>

#### wheretostart\_tempdir\_batch

```python
@contextlib.contextmanager
def wheretostart_tempdir_batch(folder: str, batch: Optional[str] = None, tempdir: Optional[str] = None) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L271)

Get a temporary directory and batch id. Deletes any existing folder if WHERETOSTART environment variable is set
to RESET. Yields a dictionary with key folder which is the temporary directory optionally with folder appended
(and created if it doesn't exist). In key batch is a batch code to be passed as the batch parameter in
create_in_hdx or update_in_hdx calls.

**Arguments**:

- `folder` _str_ - Folder to create in temporary folder
- `batch` _Optional[str]_ - Batch to use if there isn't one in a file already.
- `tempdir` _Optional[str]_ - Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).
  

**Returns**:

- `Dict` - Dictionary containing temporary directory in key folder and batch id in key batch

<a id="hdx.utilities.path.progress_storing_tempdir"></a>

#### progress\_storing\_tempdir

```python
def progress_storing_tempdir(folder: str, iterator: Iterable[Dict], key: str, batch: Optional[str] = None, tempdir: Optional[str] = None) -> Tuple[Dict, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L306)

Store progress in temporary directory. The folder persists until the final iteration allowing which iteration to
start at and the batch code to be persisted between runs. Yields 2 dictionaries. The first contains key folder which
is the temporary directory optionally with folder appended (and created if it doesn't exist). In key progress is
held the current position in the iterator. It also contains the key batch containing a batch code to be passed as
the batch parameter in create_in_hdx or update_in_hdx calls. The second dictionary is the next dictionary in the
iterator. The WHERETOSTART environment variable can be set to RESET to force the deletion and recreation of the
temporary directory or to a key value pair in the form key=value eg. iso3=PAK indicating where to start.

**Arguments**:

- `folder` _str_ - Folder to create in temporary folder
- `iterator` _Iterable[Dict]_ - Iterate over the iterator persisting progress
- `key` _str_ - Key to examine from dictionary from iterator
- `batch` _Optional[str]_ - Batch to use if there isn't one in a file already.
- `tempdir` _Optional[str]_ - Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).
  

**Returns**:

- `Tuple[Dict,Dict]` - A tuple of the form (info dictionary, next object in iterator)

<a id="hdx.utilities.path.multiple_progress_storing_tempdir"></a>

#### multiple\_progress\_storing\_tempdir

```python
def multiple_progress_storing_tempdir(folder: str, iterators: List[Iterable[Dict]], keys: List[str], batch: Optional[str] = None) -> Tuple[Dict, Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L337)

Store progress in temporary directory. The folder persists until the final iteration of the last iterator
allowing which iteration to start at and the batch code to be persisted between runs. Yields 2 dictionaries. The
first contains key folder which is the temporary directory optionally with folder appended (and created if it
doesn't exist). In key progress is held the current position in the iterator. It also contains the key batch
containing a batch code to be passed as the batch parameter in create_in_hdx or update_in_hdx calls. The second
dictionary is the next dictionary in the iterator. The WHERETOSTART environment variable can be set to RESET to
force the deletion and recreation of the temporary directory or to a key value pair in the form key=value eg.
iso3=PAK indicating where to start.

**Arguments**:

- `folder` _str_ - Folder to create in temporary folder
- `iterators` _List[Iterable[Dict]_ - Iterate over each iterator in the list consecutively persisting progress
- `keys` _List[str]_ - Key to examine from dictionary from each iterator in the above list
- `batch` _Optional[str]_ - Batch to use if there isn't one in a file already.
  

**Returns**:

  Tuple[int, Dict,Dict]: A tuple of the form (iterator index, info dictionary, next object in iterator)

<a id="hdx.utilities.path.get_filename_from_url"></a>

#### get\_filename\_from\_url

```python
def get_filename_from_url(url: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L407)

Get filename including extension from url

**Arguments**:

- `url` _str_ - URL
  

**Returns**:

- `str` - filename

<a id="hdx.utilities.path.get_filename_extension_from_url"></a>

#### get\_filename\_extension\_from\_url

```python
def get_filename_extension_from_url(url: str) -> Tuple[str, str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/path.py#L421)

Get separately filename and extension from url

**Arguments**:

- `url` _str_ - URL to download
  

**Returns**:

- `Tuple[str,str]` - Tuple of (filename, extension)

<a id="hdx.utilities.compare"></a>

# hdx.utilities.compare

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/compare.py#L1)

File compare utilities

<a id="hdx.utilities.compare.compare_files"></a>

#### compare\_files

```python
def compare_files(path1: str, path2: str) -> List[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/compare.py#L7)

Returns the delta between two files using -, ?, + format excluding
lines that are the same

**Arguments**:

- `path1` _str_ - Path to first file
- `path2` _str_ - Path to second file
  

**Returns**:

- `List[str]` - Delta between the two files

<a id="hdx.utilities.compare.assert_files_same"></a>

#### assert\_files\_same

```python
def assert_files_same(path1: str, path2: str) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/compare.py#L25)

Asserts that two files are the same and returns delta using
-, ?, + format if not

**Arguments**:

- `path1` _str_ - Path to first file
- `path2` _str_ - Path to second file
  

**Returns**:

  None

<a id="hdx.utilities.dictandlist"></a>

# hdx.utilities.dictandlist

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L1)

Dict and List utilities

<a id="hdx.utilities.dictandlist.merge_two_dictionaries"></a>

#### merge\_two\_dictionaries

```python
def merge_two_dictionaries(a: DictUpperBound, b: DictUpperBound, merge_lists: bool = False) -> DictUpperBound
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L13)

Merges b into a and returns merged result

NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen

**Arguments**:

- `a` _DictUpperBound_ - dictionary to merge into
- `b` _DictUpperBound_ - dictionary to merge from
- `merge_lists` _bool_ - Whether to merge lists (True) or replace lists (False). Default is False.
  

**Returns**:

- `DictUpperBound` - Merged dictionary

<a id="hdx.utilities.dictandlist.merge_dictionaries"></a>

#### merge\_dictionaries

```python
def merge_dictionaries(dicts: List[DictUpperBound], merge_lists: bool = False) -> DictUpperBound
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L70)

Merges all dictionaries in dicts into a single dictionary and returns result

**Arguments**:

- `dicts` _List[DictUpperBound]_ - Dictionaries to merge into the first one in the list
- `merge_lists` _bool_ - Whether to merge lists (True) or replace lists (False). Default is False.
  

**Returns**:

- `DictUpperBound` - Merged dictionary

<a id="hdx.utilities.dictandlist.dict_diff"></a>

#### dict\_diff

```python
def dict_diff(d1: DictUpperBound, d2: DictUpperBound, no_key: str = "<KEYNOTFOUND>") -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L89)

Compares two dictionaries

**Arguments**:

- `d1` _DictUpperBound_ - First dictionary to compare
- `d2` _DictUpperBound_ - Second dictionary to compare
- `no_key` _str_ - What value to use if key is not found Defaults to '<KEYNOTFOUND>'.
  

**Returns**:

- `Dict` - Comparison dictionary

<a id="hdx.utilities.dictandlist.dict_of_lists_add"></a>

#### dict\_of\_lists\_add

```python
def dict_of_lists_add(dictionary: DictUpperBound, key: Any, value: Any) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L112)

Add value to a list in a dictionary by key

**Arguments**:

- `dictionary` _DictUpperBound_ - Dictionary to which to add values
- `key` _Any_ - Key within dictionary
- `value` _Any_ - Value to add to list in dictionary
  

**Returns**:

  None

<a id="hdx.utilities.dictandlist.dict_of_sets_add"></a>

#### dict\_of\_sets\_add

```python
def dict_of_sets_add(dictionary: DictUpperBound, key: Any, value: Any) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L131)

Add value to a set in a dictionary by key

**Arguments**:

- `dictionary` _DictUpperBound_ - Dictionary to which to add values
- `key` _Any_ - Key within dictionary
- `value` _Any_ - Value to add to set in dictionary
  

**Returns**:

  None

<a id="hdx.utilities.dictandlist.dict_of_dicts_add"></a>

#### dict\_of\_dicts\_add

```python
def dict_of_dicts_add(dictionary: DictUpperBound, parent_key: Any, key: Any, value: Any) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L148)

Add key value pair to a dictionary within a dictionary by key

**Arguments**:

- `dictionary` _DictUpperBound_ - Dictionary to which to add values
- `parent_key` _Any_ - Key within parent dictionary
- `key` _Any_ - Key within dictionary
- `value` _Any_ - Value to add to set in dictionary
  

**Returns**:

  None

<a id="hdx.utilities.dictandlist.list_distribute_contents_simple"></a>

#### list\_distribute\_contents\_simple

```python
def list_distribute_contents_simple(input_list: List, function: Callable[[Any], Any] = lambda x: x) -> List
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L168)

Distribute the contents of a list eg. [1, 1, 1, 2, 2, 3] -> [1, 2, 3, 1, 2, 1]. List can contain complex types
like dictionaries in which case the function can return the appropriate value eg.  lambda x: x[KEY]

**Arguments**:

- `input_list` _List_ - List to distribute values
- `function` _Callable[[Any], Any]_ - Return value to use for distributing. Defaults to lambda x: x.
  

**Returns**:

- `List` - Distributed list

<a id="hdx.utilities.dictandlist.list_distribute_contents"></a>

#### list\_distribute\_contents

```python
def list_distribute_contents(input_list: List, function: Callable[[Any], Any] = lambda x: x) -> List
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L201)

Distribute the contents of a list eg. [1, 1, 1, 2, 2, 3] -> [1, 2, 1, 2, 1, 3]. List can contain complex types
like dictionaries in which case the function can return the appropriate value eg.  lambda x: x[KEY]

**Arguments**:

- `input_list` _List_ - List to distribute values
- `function` _Callable[[Any], Any]_ - Return value to use for distributing. Defaults to lambda x: x.
  

**Returns**:

- `List` - Distributed list

<a id="hdx.utilities.dictandlist.extract_list_from_list_of_dict"></a>

#### extract\_list\_from\_list\_of\_dict

```python
def extract_list_from_list_of_dict(list_of_dict: List[DictUpperBound], key: Any) -> List
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L250)

Extract a list by looking up key in each member of a list of dictionaries

**Arguments**:

- `list_of_dict` _List[DictUpperBound]_ - List of dictionaries
- `key` _Any_ - Key to find in each dictionary
  

**Returns**:

- `List` - List containing values returned from each dictionary

<a id="hdx.utilities.dictandlist.key_value_convert"></a>

#### key\_value\_convert

```python
def key_value_convert(dictin: DictUpperBound, keyfn: Callable[[Any], Any] = lambda x: x, valuefn: Callable[[Any], Any] = lambda x: x, dropfailedkeys: bool = False, dropfailedvalues: bool = False, exception: ExceptionUpperBound = ValueError) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L269)

Convert keys and/or values of dictionary using functions passed in as parameters

**Arguments**:

- `dictin` _DictUpperBound_ - Input dictionary
- `keyfn` _Callable[[Any], Any]_ - Function to convert keys. Defaults to lambda x: x
- `valuefn` _Callable[[Any], Any]_ - Function to convert values. Defaults to lambda x: x
- `dropfailedkeys` _bool_ - Whether to drop dictionary entries where key conversion fails. Defaults to False.
- `dropfailedvalues` _bool_ - Whether to drop dictionary entries where value conversion fails. Defaults to False.
- `exception` _ExceptionUpperBound_ - The exception to expect if keyfn or valuefn fail. Defaults to ValueError.
  

**Returns**:

- `Dict` - Dictionary with converted keys and/or values

<a id="hdx.utilities.dictandlist.integer_key_convert"></a>

#### integer\_key\_convert

```python
def integer_key_convert(dictin: DictUpperBound, dropfailedkeys: bool = False) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L310)

Convert keys of dictionary to integers

**Arguments**:

- `dictin` _DictUpperBound_ - Input dictionary
- `dropfailedkeys` _bool_ - Whether to drop dictionary entries where key conversion fails. Defaults to False.
  

**Returns**:

- `Dict` - Dictionary with keys converted to integers

<a id="hdx.utilities.dictandlist.integer_value_convert"></a>

#### integer\_value\_convert

```python
def integer_value_convert(dictin: DictUpperBound, dropfailedvalues: bool = False) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L326)

Convert values of dictionary to integers

**Arguments**:

- `dictin` _DictUpperBound_ - Input dictionary
- `dropfailedvalues` _bool_ - Whether to drop dictionary entries where key conversion fails. Defaults to False.
  

**Returns**:

- `Dict` - Dictionary with values converted to integers

<a id="hdx.utilities.dictandlist.float_value_convert"></a>

#### float\_value\_convert

```python
def float_value_convert(dictin: DictUpperBound, dropfailedvalues: bool = False) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L344)

Convert values of dictionary to floats

**Arguments**:

- `dictin` _DictUpperBound_ - Input dictionary
- `dropfailedvalues` _bool_ - Whether to drop dictionary entries where key conversion fails. Defaults to False.
  

**Returns**:

- `Dict` - Dictionary with values converted to floats

<a id="hdx.utilities.dictandlist.avg_dicts"></a>

#### avg\_dicts

```python
def avg_dicts(dictin1: DictUpperBound, dictin2: DictUpperBound, dropmissing: bool = True) -> Dict
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L362)

Create a new dictionary from two dictionaries by averaging values

**Arguments**:

- `dictin1` _DictUpperBound_ - First input dictionary
- `dictin2` _DictUpperBound_ - Second input dictionary
- `dropmissing` _bool_ - Whether to drop keys missing in one dictionary. Defaults to True.
  

**Returns**:

- `Dict` - Dictionary with values being average of 2 input dictionaries

<a id="hdx.utilities.dictandlist.read_list_from_csv"></a>

#### read\_list\_from\_csv

```python
def read_list_from_csv(url: str, headers: Union[int, List[int], List[str], None] = None, dict_form: bool = False, **kwargs: Any, ,) -> List[Union[Dict, List]]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L389)

Read a list of rows in dict or list form from a csv. The headers argument is either a row
number or list of row numbers (in case of multi-line headers) to be considered as headers
(rows start counting at 1), or the actual headers defined a list of strings. If not set,
all rows will be treated as containing values.

**Arguments**:

- `url` _str_ - URL or path to read from
- `headers` _Union[int, List[int], List[str], None]_ - Row number of headers. Defaults to None.
- `dict_form` _bool_ - Return dict (requires headers parameter) or list for each row. Defaults to False (list)
- `**kwargs` - Other arguments to pass to Tabulator Stream
  

**Returns**:

  List[Union[Dict, List]]: List of rows in dict or list form

<a id="hdx.utilities.dictandlist.write_list_to_csv"></a>

#### write\_list\_to\_csv

```python
def write_list_to_csv(filepath: str, list_of_rows: List[Union[DictUpperBound, List]], headers: Union[int, List[int], List[str], None] = None) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L419)

Write a list of rows in dict or list form to a csv. (The headers argument is either a row
number or list of row numbers (in case of multi-line headers) to be considered as headers
(rows start counting at 1), or the actual headers defined a list of strings. If not set,
all rows will be treated as containing values.)

**Arguments**:

- `filepath` _str_ - Path to write to
- `list_of_rows` _List[Union[DictUpperBound, List]]_ - List of rows in dict or list form
- `headers` _Union[int, List[int], List[str], None]_ - Headers to write. Defaults to None.
  

**Returns**:

  None

<a id="hdx.utilities.dictandlist.args_to_dict"></a>

#### args\_to\_dict

```python
def args_to_dict(args: str) -> DictUpperBound
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dictandlist.py#L444)

Convert command line arguments in a comma separated string to a dictionary

**Arguments**:

- `args` _str_ - Command line arguments
  

**Returns**:

- `DictUpperBound` - Dictionary of arguments

<a id="hdx.utilities.encoding"></a>

# hdx.utilities.encoding

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/encoding.py#L1)

Encoding utilities

<a id="hdx.utilities.encoding.str_to_base64"></a>

#### str\_to\_base64

```python
def str_to_base64(string: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/encoding.py#L6)

Base 64 encode string

**Arguments**:

- `string` _str_ - String to encode
  

**Returns**:

- `str` - Base 64 encoded string

<a id="hdx.utilities.encoding.base64_to_str"></a>

#### base64\_to\_str

```python
def base64_to_str(bstring: str) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/encoding.py#L20)

Base 64 decode string

**Arguments**:

- `bstring` _str_ - Base 64 encoded string to encode
  

**Returns**:

- `str` - Decoded string

<a id="hdx.utilities.easy_logging"></a>

# hdx.utilities.easy\_logging

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/easy_logging.py#L1)

Configuration of logging

<a id="hdx.utilities.easy_logging.setup_logging"></a>

#### setup\_logging

```python
def setup_logging(**kwargs: Any) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/easy_logging.py#L15)

Setup logging configuration

**Arguments**:

- `**kwargs` - See below
- `logging_config_dict` _dict_ - Logging configuration dictionary OR
- `logging_config_json` _str_ - Path to JSON Logging configuration OR
- `logging_config_yaml` _str_ - Path to YAML Logging configuration. Defaults to internal logging_configuration.yml.
- `smtp_config_dict` _dict_ - Email Logging configuration dictionary if using default logging configuration OR
- `smtp_config_json` _str_ - Path to JSON Email Logging configuration if using default logging configuration OR
- `smtp_config_yaml` _str_ - Path to YAML Email Logging configuration if using default logging configuration
  

**Returns**:

  None

<a id="hdx.utilities.email"></a>

# hdx.utilities.email

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L1)

Utility class to simplify sending emails

<a id="hdx.utilities.email.Email"></a>

## Email Objects

```python
class Email()
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L21)

Emailer utility. Parameters in dictionary or file (eg. yaml below):
| connection_type: "ssl"   ("ssl" for smtp ssl or "lmtp", otherwise basic smtp is assumed)
| host: "localhost"
| port: 123
| local_hostname: "mycomputer.fqdn.com"
| timeout: 3
| username: "user"
| password: "pass"
| sender: "a@b.com"    (if not supplied username is used as sender)

**Arguments**:

- `**kwargs` - See below
- `email_config_dict` _dict_ - HDX configuration dictionary OR
- `email_config_json` _str_ - Path to JSON HDX configuration OR
- `email_config_yaml` _str_ - Path to YAML HDX configuration. Defaults to ~/hdx_email_configuration.yml.

<a id="hdx.utilities.email.Email.__enter__"></a>

#### \_\_enter\_\_

```python
def __enter__() -> "Email"
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L91)

Return Email object for with statement

**Returns**:

  None

<a id="hdx.utilities.email.Email.__exit__"></a>

#### \_\_exit\_\_

```python
def __exit__(*args: Any) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L101)

Close Email object for end of with statement

**Arguments**:

- `*args` - Not used
  

**Returns**:

  None

<a id="hdx.utilities.email.Email.connect"></a>

#### connect

```python
def connect() -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L113)

Connect to server

**Returns**:

  None

<a id="hdx.utilities.email.Email.close"></a>

#### close

```python
def close() -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L146)

Close connection to email server

**Returns**:

  None

<a id="hdx.utilities.email.Email.get_normalised_emails"></a>

#### get\_normalised\_emails

```python
@staticmethod
def get_normalised_emails(recipients: List[str]) -> List[str]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L157)

Get list of normalised emails

**Arguments**:

- `recipients` _List[str]_ - Email recipient
  

**Returns**:

- `List[str]` - Normalised emails

<a id="hdx.utilities.email.Email.send"></a>

#### send

```python
def send(recipients: List[str], subject: str, text_body: str, html_body: Optional[str] = None, sender: Optional[str] = None, cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None, **kwargs: Any, ,) -> None
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/email.py#L178)

Send email

**Arguments**:

- `recipients` _List[str]_ - Email recipient
- `subject` _str_ - Email subject
- `text_body` _str_ - Plain text email body
- `html_body` _Optional[str]_ - HTML email body
- `sender` _Optional[str]_ - Email sender. Defaults to global sender.
- `cc` _Optional[List[str]]_ - Email cc. Defaults to None.
- `bcc` _Optional[List[str]]_ - Email cc. Defaults to None.
- `**kwargs` - See below
- `mail_options` _list_ - Mail options (see smtplib documentation)
- `rcpt_options` _list_ - Recipient options (see smtplib documentation)
  

**Returns**:

  None

<a id="hdx.utilities.dateparse"></a>

# hdx.utilities.dateparse

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L1)

Date parsing utilities

<a id="hdx.utilities.dateparse.parse"></a>

#### parse

```python
def parse(timestr, default=None, ignoretz=False, tzinfos=None, **kwargs)
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L477)

Parse the date/time string into a :class:`datetime.datetime` object.

**Arguments**:

    Any date/time string using the supported formats.

    The default datetime object, if this is a datetime object and not
    ``None``, elements specified in ``timestr`` replace elements in the
    default object.

    If set ``True``, time zones in parsed strings are ignored and a
    naive :class:`datetime.datetime` object is returned.

    Additional time zone names / aliases which may be present in the
    string. This argument maps time zone names (and optionally offsets
    from those time zones) to time zones. This parameter can be a
    dictionary with timezone aliases mapping time zone names to time
    zones or a function taking two parameters (``tzname`` and
    ``tzoffset``) and returning a time zone.

    The timezones to which the names are mapped can be an integer
    offset from UTC in seconds or a :class:`tzinfo` object.

    .. doctest::
       :options: +NORMALIZE_WHITESPACE

        >>> from dateutil.parser import parse
        >>> from dateutil.tz import gettz
        >>> tzinfos = {"BRST": -7200, "CST": gettz("America/Chicago")}
        >>> parse("2012-01-19 17:21:00 BRST", tzinfos=tzinfos)
        datetime.datetime(2012, 1, 19, 17, 21, tzinfo=tzoffset(u'BRST', -7200))
        >>> parse("2012-01-19 17:21:00 CST", tzinfos=tzinfos)
        datetime.datetime(2012, 1, 19, 17, 21,
                          tzinfo=tzfile('/usr/share/zoneinfo/America/Chicago'))

    This parameter is ignored if ``ignoretz`` is set.

:param \\*\\*kwargs:
    Keyword arguments as passed to ``_parse()``.

- `timestr`: 
- `default`: 
- `ignoretz`: 
- `tzinfos`: 

**Returns**:


**Raises**:

- `ParserError`: 
    Raised for invalid or unknown string format, if the provided
    :class:`tzinfo` is not in a valid format, or if an invalid date
    would be created.

- `TypeError`: 
    Raised for non-string or character stream input.

- `OverflowError`: 
    Raised if the parsed date exceeds the largest valid C integer on
    your system.

<a id="hdx.utilities.dateparse.parse_date_range"></a>

#### parse\_date\_range

```python
def parse_date_range(string: str, date_format: Optional[str] = None, fuzzy: Optional[Dict] = None, zero_time: bool = False) -> Tuple[datetime, datetime]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L569)

Parse date from string using specified format (setting any time elements to 0 if zero_time is True).
If no format is supplied, the function will guess. For unambiguous formats, this should be fine.
Returns date range in dictionary keys startdate and enddate. If a dictionary is supplied in the fuzzy parameter,
then dateutil's fuzzy parsing is used and the results returned in the dictionary in keys startdate, enddate,
date (the string elements used to make the date) and nondate (the non date part of the string).

**Arguments**:

- `string` _str_ - Dataset date string
- `date_format` _Optional[str]_ - Date format. If None is given, will attempt to guess. Defaults to None.
- `fuzzy` _Optional[Dict]_ - If dict supplied, fuzzy matching will be used and results returned in dict
- `zero_time` _bool_ - Zero time elements of datetime if True. Defaults to False.
  

**Returns**:

- `Tuple[datetime,datetime]` - Tuple containing start date and end date

<a id="hdx.utilities.dateparse.parse_date"></a>

#### parse\_date

```python
def parse_date(string: str, date_format: Optional[str] = None, fuzzy: Optional[Dict] = None, zero_time: bool = False) -> datetime
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L652)

Parse date from string using specified format (setting any time elements to 0 if zero_time is True).
If no format is supplied, the function will guess. For unambiguous formats, this should be fine.
Returns a datetime object. Raises exception for dates that are missing year, month or day.
If a dictionary is supplied in the fuzzy parameter, then dateutil's fuzzy parsing is used and the results
returned in the dictionary in keys startdate, enddate, date (the string elements used to make the date) and
nondate (the non date part of the string).

**Arguments**:

- `string` _str_ - Dataset date string
- `date_format` _Optional[str]_ - Date format. If None is given, will attempt to guess. Defaults to None.
- `fuzzy` _Optional[Dict]_ - If dict supplied, fuzzy matching will be used and results returned in dict
- `zero_time` _bool_ - Zero time elements of datetime if True. Defaults to False.
  

**Returns**:

- `datetime` - The parsed date

<a id="hdx.utilities.dateparse.get_timestamp_from_datetime"></a>

#### get\_timestamp\_from\_datetime

```python
def get_timestamp_from_datetime(date: datetime) -> float
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L682)

Convert datetime to timestamp.

**Arguments**:

- `date` _datetime_ - Date to convert
  

**Returns**:

- `float` - Timestamp

<a id="hdx.utilities.dateparse.get_datetime_from_timestamp"></a>

#### get\_datetime\_from\_timestamp

```python
def get_datetime_from_timestamp(timestamp: float, timezone: datetime.tzinfo = tzutc, today: datetime = datetime.now(tzutc())) -> datetime
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/dateparse.py#L712)

Convert timestamp to datetime.

**Arguments**:

- `timestamp` _float_ - Timestamp to convert
- `timezone` _datetime.tzinfo_ - Timezone to use
- `today` _datetime_ - Today's date. Defaults to datetime.now().
  

**Returns**:

- `datetime` - Date of timestamp

<a id="hdx.utilities.html"></a>

# hdx.utilities.html

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/html.py#L1)

HTML parsing utilities

<a id="hdx.utilities.html.get_soup"></a>

#### get\_soup

```python
def get_soup(url: str, downloader: Download = None, user_agent: Optional[str] = None, user_agent_config_yaml: Optional[str] = None, user_agent_lookup: Optional[str] = None, **kwargs: Any, ,) -> BeautifulSoup
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/html.py#L13)

Get BeautifulSoup object for a url. Requires either global user agent to be set or appropriate user agent
parameter(s) to be completed.

**Arguments**:

- `url` _str_ - url to read
- `downloader` _Download_ - Download object. Defaults to creating a Download object with given user agent values.
- `user_agent` _Optional[str]_ - User agent string. HDXPythonUtilities/X.X.X- is prefixed.
- `user_agent_config_yaml` _Optional[str]_ - Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
- `user_agent_lookup` _Optional[str]_ - Lookup key for YAML. Ignored if user_agent supplied.
  

**Returns**:

- `BeautifulSoup` - The BeautifulSoup object for a url

<a id="hdx.utilities.html.get_text"></a>

#### get\_text

```python
def get_text(tag: Tag) -> str
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/html.py#L44)

Get text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

**Arguments**:

- `tag` _Tag_ - BeautifulSoup tag
  

**Returns**:

- `str` - Text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

<a id="hdx.utilities.html.extract_table"></a>

#### extract\_table

```python
def extract_table(tabletag: Tag) -> List[Dict]
```

[[view_source]](https://github.com/OCHA-DAP/hdx-python-utilities/blob/a67800c92ddb61afd7b569af33c6f30218b9e0d5/src/hdx/utilities/html.py#L58)

Extract HTML table as list of dictionaries

**Arguments**:

- `tabletag` _Tag_ - BeautifulSoup tag
  

**Returns**:

- `str` - Text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

