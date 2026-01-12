"""Directory Path Utilities."""

import contextlib
import inspect
import logging
import sys
from collections.abc import Generator, Iterable, Sequence
from os import getenv, makedirs, remove
from os.path import (
    abspath,
    basename,
    dirname,
    exists,
    join,
    realpath,
    splitext,
)
from shutil import rmtree
from tempfile import gettempdir
from typing import Any
from urllib.parse import unquote_plus, urlsplit

from slugify import slugify

from hdx.utilities.loader import load_text
from hdx.utilities.saver import save_text
from hdx.utilities.uuid import get_uuid

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def script_dir(pyobject: Any, follow_symlinks: bool = True) -> str:
    """Get current script's directory.

    Args:
        pyobject: Any Python object in the script
        follow_symlinks: Follow symlinks or not. Defaults to True.

    Returns:
        Current script's directory
    """
    if getattr(sys, "frozen", False):  # py2exe, PyInstaller, cx_Freeze
        path = abspath(sys.executable)  # pragma: no cover
    else:
        path = inspect.getabsfile(pyobject)
    if follow_symlinks:
        path = realpath(path)
    return dirname(path)


def script_dir_plus_file(
    filename: str, pyobject: Any, follow_symlinks: bool = True
) -> str:
    """Get current script's directory and then append a filename.

    Args:
        filename: Filename to append to directory path
        pyobject: Any Python object in the script
        follow_symlinks: Follow symlinks or not. Defaults to True.

    Returns:
        Current script's directory and with filename appended
    """
    return join(script_dir(pyobject, follow_symlinks), filename)


def get_temp_dir(
    folder: str | None = None,
    delete_if_exists: bool = False,
    tempdir: str | None = None,
) -> str:
    """Get a temporary directory. Looks for environment variable TEMP_DIR and
    falls back on os.gettempdir if a root temporary directory is not supplied.
    If a folder is supplied, creates that folder within the temporary
    directory. Optionally deletes and recreates it if it already exists.

    Args:
        folder: Folder to create in temporary folder. Defaults to None.
        delete_if_exists: Whether to delete the folder if it exists. Defaults to False.
        tempdir: Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        A temporary directory
    """
    if tempdir is None:
        tempdir = getenv("TEMP_DIR", gettempdir())
    if folder:
        tempdir = join(tempdir, folder)
        if exists(tempdir):
            if delete_if_exists:
                rmtree(tempdir)
                makedirs(tempdir)
        else:
            makedirs(tempdir)
    return tempdir


@contextlib.contextmanager
def temp_dir(
    folder: str | None = None,
    delete_if_exists: bool = False,
    delete_on_success: bool = True,
    delete_on_failure: bool = True,
    tempdir: str | None = None,
) -> Generator[str, Any, None]:
    """Get a temporary directory optionally with folder appended (and created
    if it doesn't exist)

    Args:
        folder: Folder to create in temporary folder. Defaults to None.
        delete_if_exists: Whether to delete the folder if it exists. Defaults to False.
        delete_on_success: Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
        delete_on_failure: Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
        tempdir: Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        A temporary directory
    """
    tempdir = get_temp_dir(folder, delete_if_exists=delete_if_exists, tempdir=tempdir)
    try:
        yield tempdir
        if folder and delete_on_success:
            rmtree(tempdir)
    except Exception as ex:
        if not isinstance(ex, NotFoundError):
            if folder and delete_on_failure:
                rmtree(tempdir)
            raise


def read_or_create_batch(folder: str, batch: str | None = None) -> str:
    """Get batch or create it if it doesn't exist.

    Args:
        folder: Folder in which to look for or create batch file.
        batch: Batch to use if there isn't one in a file already.

    Returns:
        Batch
    """
    batch_file = join(folder, "batch.txt")
    if exists(batch_file):
        batch = load_text(batch_file, strip=True)
        logger.info(f"File BATCH = {batch}")
    else:
        if not batch:
            batch = get_uuid()
            logger.info(f"Generated BATCH = {batch}")
        save_text(batch, batch_file)
    return batch


@contextlib.contextmanager
def temp_dir_batch(
    folder: str | None = None,
    delete_if_exists: bool = False,
    delete_on_success: bool = True,
    delete_on_failure: bool = True,
    batch: str | None = None,
    tempdir: str | None = None,
) -> Generator[dict, Any, None]:
    """Get a temporary directory and batch id. Yields a dictionary with key
    folder which is the temporary directory optionally with folder appended
    (and created if it doesn't exist). In key batch is a batch code to be
    passed as the batch parameter in create_in_hdx or update_in_hdx calls.

    Args:
        folder: Folder to create in temporary folder. Defaults to None.
        delete_if_exists: Whether to delete the folder if it exists. Defaults to False.
        delete_on_success: Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
        delete_on_failure: Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
        batch: Batch to use if there isn't one in a file already.
        tempdir: Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        Dictionary containing temporary directory in key folder and batch id in key batch
    """
    with temp_dir(
        folder,
        delete_if_exists,
        delete_on_success,
        delete_on_failure,
        tempdir=tempdir,
    ) as tempdir:
        yield {
            "folder": tempdir,
            "batch": read_or_create_batch(tempdir, batch),
        }


def get_wheretostart(text: str, message: str, key: str) -> str | None:
    """Evaluate WHERETOSTART.

    Args:
        text: String to process
        message: Text for logging
        key: Key to comapre with

    Returns:
        A string or None
    """
    upper_text = text.upper()
    if upper_text == "RESET":
        return None
    w_key, wheretostart = text.split("=")
    if w_key == key:
        logger.info(f"{message} WHERETOSTART = {wheretostart}")
        return wheretostart
    else:
        return "IGNORE"


def progress_storing_folder(
    info: dict,
    iterator: Iterable[dict],
    key: str,
    wheretostart: str | None = None,
) -> Generator[tuple[dict, dict], Any, None]:
    """Store progress in folder in key folder of info dictionary parameter.
    Yields 2 dictionaries. The first is the info dictionary. It contains in key
    folder the folder being used to store progress and in key progress the
    current position in the iterator. If store_batch is True, that dictionary
    will also contain the key batch containing a batch code to be passed as the
    batch parameter in create_in_hdx or update_in_hdx calls. The second
    dictionary is the next dictionary in the iterator.

    Args:
        info: Dictionary containing folder and anything else to be yielded
        iterator: Iterate over this object persisting progress
        key: Key to examine from dictionary from iterator
        wheretostart: Where in iterator to start

    Returns:
        A tuple of the form (info dictionary, next object in iterator)
    """
    folder = info["folder"]
    progress_file = join(folder, "progress.txt")

    if not wheretostart:
        contents = getenv("WHERETOSTART")
        if contents:
            wheretostart = get_wheretostart(contents, "Environment variable", key)
        else:
            if exists(progress_file):
                contents = load_text(progress_file, strip=True)
                wheretostart = get_wheretostart(contents, "File", key)
            else:
                wheretostart = None
    found = False
    for nextdict in iterator:
        current = nextdict[key]
        if wheretostart:
            if wheretostart == "IGNORE":
                continue
            if not found:
                if current == wheretostart:
                    found = True
                    logger.info(f"Starting run from WHERETOSTART {wheretostart}")
                else:
                    logger.info(
                        f"Run not started. Ignoring {current}. WHERETOSTART ({wheretostart}) not matched."
                    )
                    continue
        output = f"{key}={current}"
        info["progress"] = output
        save_text(output, progress_file)
        yield info, nextdict
    if wheretostart and not found:
        raise NotFoundError(
            f"WHERETOSTART ({wheretostart}) not matched in iterator with key {key} and no run started!"
        )


@contextlib.contextmanager
def wheretostart_tempdir_batch(
    folder: str, batch: str | None = None, tempdir: str | None = None
) -> Generator[dict, Any, None]:
    """Get a temporary directory and batch id. Deletes any existing folder if
    WHERETOSTART environment variable is set to RESET. Yields a dictionary with
    key folder which is the temporary directory optionally with folder appended
    (and created if it doesn't exist). In key batch is a batch code to be
    passed as the batch parameter in create_in_hdx or update_in_hdx calls.

    Args:
        folder: Folder to create in temporary folder
        batch: Batch to use if there isn't one in a file already.
        tempdir: Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        Dictionary containing temporary directory in key folder and batch id in key batch
    """
    delete_if_exists = False
    wheretostart = getenv("WHERETOSTART")
    if wheretostart:
        if wheretostart.upper() == "RESET":
            delete_if_exists = True
            logger.info("Removing progress file and will start from beginning!")
    with temp_dir_batch(
        folder,
        delete_if_exists,
        delete_on_success=True,
        delete_on_failure=False,
        batch=batch,
        tempdir=tempdir,
    ) as info:
        yield info


def progress_storing_tempdir(
    folder: str,
    iterator: Iterable[dict],
    key: str,
    batch: str | None = None,
    tempdir: str | None = None,
) -> Generator[tuple[dict, dict], Any, None]:
    """Store progress in temporary directory. The folder persists until the
    final iteration allowing which iteration to start at and the batch code to
    be persisted between runs. Yields 2 dictionaries. The first contains key
    folder which is the temporary directory optionally with folder appended
    (and created if it doesn't exist). In key progress is held the current
    position in the iterator. It also contains the key batch containing a batch
    code to be passed as the batch parameter in create_in_hdx or update_in_hdx
    calls. The second dictionary is the next dictionary in the iterator. The
    WHERETOSTART environment variable can be set to RESET to force the deletion
    and recreation of the temporary directory or to a key value pair in the
    form key=value eg. iso3=PAK indicating where to start.

    Args:
        folder: Folder to create in temporary folder
        iterator: Iterate over the iterator persisting progress
        key: Key to examine from dictionary from iterator
        batch: Batch to use if there isn't one in a file already.
        tempdir: Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        A tuple of the form (info dictionary, next object in iterator)
    """
    with wheretostart_tempdir_batch(folder, batch=batch, tempdir=tempdir) as info:
        yield from progress_storing_folder(info, iterator, key)


def multiple_progress_storing_tempdir(
    folder: str,
    iterators: Sequence[Iterable[dict]],
    keys: Sequence[str],
    batch: str | None = None,
) -> Generator[tuple[int, dict, dict], Any, None]:
    """Store progress in temporary directory. The folder persists until the
    final iteration of the last iterator allowing which iteration to start at
    and the batch code to be persisted between runs. Yields 2 dictionaries. The
    first contains key folder which is the temporary directory optionally with
    folder appended (and created if it doesn't exist). In key progress is held
    the current position in the iterator. It also contains the key batch
    containing a batch code to be passed as the batch parameter in
    create_in_hdx or update_in_hdx calls. The second dictionary is the next
    dictionary in the iterator. The WHERETOSTART environment variable can be
    set to RESET to force the deletion and recreation of the temporary
    directory or to a key value pair in the form key=value eg. iso3=PAK
    indicating where to start.

    Args:
        folder: Folder to create in temporary folder
        iterators: Iterate over each iterator in the list consecutively persisting progress
        keys: Key to examine from dictionary from each iterator in the above list
        batch: Batch to use if there isn't one in a file already.

    Returns:
        A tuple of the form (iterator index, info dictionary, next object in iterator)
    """
    delete_if_exists = False
    wheretostartenv = getenv("WHERETOSTART")
    if wheretostartenv:
        if wheretostartenv.upper() == "RESET":
            delete_if_exists = True
            logger.info("Removing progress file and will start from beginning!")
    with temp_dir_batch(
        folder,
        delete_if_exists,
        delete_on_success=True,
        delete_on_failure=False,
        batch=batch,
    ) as info:
        tempdir = info["folder"]
        batch = info["batch"]
        for i, key in enumerate(keys):
            progress_file = join(tempdir, "progress.txt")
            if wheretostartenv:
                wheretostart = get_wheretostart(
                    wheretostartenv, "Environment variable", key
                )
            else:
                if exists(progress_file):
                    contents = load_text(progress_file, strip=True)
                    wheretostart = get_wheretostart(contents, "File", key)
                else:
                    wheretostart = None
            with temp_dir_batch(
                str(i),
                False,
                delete_on_success=True,
                delete_on_failure=False,
                batch=batch,
                tempdir=tempdir,
            ) as info:
                for info, nextdict in progress_storing_folder(
                    info, iterators[i], key, wheretostart
                ):
                    save_text(info["progress"], progress_file)
                    yield i, info, nextdict
                if exists(progress_file):
                    remove(progress_file)


def get_filename_extension_from_url(
    url: str, second_last: bool = False, use_query: bool = False
) -> tuple[str, str]:
    """Get separately filename and extension from url.

    Args:
        url: URL to download
        second_last: Get second last segment of url as well. Defaults to False.
        use_query: Include query parameters as well. Defaults to False.

    Returns:
        Tuple of (filename, extension)
    """
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
    url: str, second_last: bool = False, use_query: bool = False
) -> str:
    """Get filename including extension from url.

    Args:
        url: URL
        second_last: Get second last segment of url as well. Defaults to False.
        use_query: Include query parameters as well. Defaults to False.

    Returns:
        filename
    """
    filename, extension = get_filename_extension_from_url(url, second_last, use_query)
    return f"{filename}{extension}"
