"""URL processing utilities."""

from os import remove
from os.path import basename, dirname, exists, split, splitext
from pathlib import Path
from urllib.parse import parse_qsl, unquote_plus, urlsplit, urlunsplit

from requests import Request
from slugify import slugify

from hdx.utilities.path import get_temp_dir


def get_filename_extension_from_url(
    url: Path | str, second_last: bool = False, use_query: bool = False
) -> tuple[str, str]:
    """Get separately filename and extension from url.

    Args:
        url: URL or path to download
        second_last: Get second last segment of url as well. Defaults to False.
        use_query: Include query parameters as well. Defaults to False.

    Returns:
        Tuple of (filename, extension)
    """
    url = str(url)
    split_url = urlsplit(unquote_plus(url))
    urlpath = split_url.path
    last_part = basename(urlpath)
    second_last_part = basename(dirname(urlpath))
    query_part = slugify(split_url.query)
    filename, extension = splitext(last_part)
    if query_part:
        if not filename:
            filename = query_part
        elif use_query:
            filename = f"{filename}_{query_part}"
    if second_last_part:
        if not filename:
            filename = second_last_part
        elif second_last:
            filename = f"{second_last_part}_{filename}"
    return filename, extension


def get_filename_from_url(
    url: Path | str, second_last: bool = False, use_query: bool = False
) -> str:
    """Get filename including extension from url.

    Args:
        url: URL or path
        second_last: Get second last segment of url as well. Defaults to False.
        use_query: Include query parameters as well. Defaults to False.

    Returns:
        filename
    """
    filename, extension = get_filename_extension_from_url(url, second_last, use_query)
    return f"{filename}{extension}"


def get_path_for_url(
    url: str,
    folder: Path | str | None = None,
    filename: str | None = None,
    path: Path | str | None = None,
    overwrite: bool = False,
    keep: bool = False,
) -> Path:
    """Get filename from url and join to provided folder or temporary
    folder if no folder supplied, ensuring uniqueness.

    Args:
        url: URL to download
        folder: Folder to download it to. Defaults to None (temporary folder).
        filename: Filename to use for downloaded file. Defaults to None (derive from the url).
        path: Full path to use for downloaded file. Defaults to None (use folder and filename).
        overwrite: Whether to overwrite existing file. Defaults to False.
        keep: Whether to keep already downloaded file. Defaults to False.

    Returns:
        Path of downloaded file
    """
    if path:
        if folder or filename:
            raise ValueError(
                "Cannot use folder or filename and path arguments together!"
            )
        folder, filename = split(path)
    if not filename:
        filename = get_filename_from_url(url)
    filename, extension = splitext(filename)
    if not folder:
        folder = get_temp_dir()
    folder = Path(folder)
    path = folder / f"{filename}{extension}"
    if overwrite:
        try:
            remove(path)
        except OSError:
            pass
    elif not keep:
        count = 0
        while exists(path):
            count += 1
            path = folder / f"{filename}{count}{extension}"
    return path


def get_url_for_get(url: str, parameters: dict | None = None) -> str:
    """Get full url for GET request including parameters.

    Args:
        url: URL to download
        parameters: Parameters to pass. Defaults to None.

    Returns:
        Full url
    """
    return Request("GET", url, params=parameters).prepare().url


def get_url_params_for_post(
    url: str, parameters: dict | None = None
) -> tuple[str, dict]:
    """Get full url for POST request and all parameters including any in
    the url.

    Args:
        url: URL to download
        parameters: Parameters to pass. Defaults to None.

    Returns:
        (Full url, parameters)
    """
    split_url = urlsplit(url)
    merged_params = dict(parse_qsl(split_url.query)) | (parameters or {})
    clean_url = urlunsplit(split_url._replace(query=""))
    return clean_url, merged_params
