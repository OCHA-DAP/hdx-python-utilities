# -*- coding: utf-8 -*-
"""Directory Path Utilities"""
import contextlib
import inspect
import logging
import sys
from os import getenv, makedirs, remove
from os.path import abspath, realpath, dirname, join, exists
from shutil import rmtree
from tempfile import gettempdir

from typing import Any, Optional, Iterable, Tuple, Dict, List

from hdx.utilities import get_uuid
from hdx.utilities.loader import load_file_to_str
from hdx.utilities.saver import save_str_to_file

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    pass


def script_dir(pyobject, follow_symlinks=True):
    # type: (Any, bool) -> str
    """Get current script's directory

    Args:
        pyobject (Any): Any Python object in the script
        follow_symlinks (bool): Follow symlinks or not. Defaults to True.

    Returns:
        str: Current script's directory
    """
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        path = abspath(sys.executable)   # pragma: no cover
    else:
        path = inspect.getabsfile(pyobject)
    if follow_symlinks:
        path = realpath(path)
    return dirname(path)


def script_dir_plus_file(filename, pyobject, follow_symlinks=True):
    # type: (str, Any, bool) -> str
    """Get current script's directory and then append a filename

    Args:
        filename (str): Filename to append to directory path
        pyobject (Any): Any Python object in the script
        follow_symlinks (bool): Follow symlinks or not. Defaults to True.

    Returns:
        str: Current script's directory and with filename appended
    """
    return join(script_dir(pyobject, follow_symlinks), filename)


def get_temp_dir(folder=None, delete_if_exists=False, tempdir=None):
    # type: (Optional[str], bool, Optional[str]) -> str
    """Get a temporary directory. Looks for environment variable TEMP_DIR and falls
    back on os.gettempdir if a root temporary directory is not supplied. If a folder is supplied, creates that folder
    within the temporary directory. Optionally deletes and recreates it if it already exists.

    Args:
        folder (Optional[str]): Folder to create in temporary folder. Defaults to None.
        delete_if_exists (bool): Whether to delete the folder if it exists. Defaults to False.
        tempdir (Optional[str]): Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        str: A temporary directory
    """
    if tempdir is None:
        tempdir = getenv('TEMP_DIR', gettempdir())
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
def temp_dir(folder=None, delete_if_exists=False, delete_on_success=True, delete_on_failure=True, tempdir=None):
    # type: (Optional[str], bool, bool, bool, Optional[str]) -> str
    """Get a temporary directory optionally with folder appended (and created if it doesn't exist)

    Args:
        folder (Optional[str]): Folder to create in temporary folder. Defaults to None.
        delete_if_exists (bool): Whether to delete the folder if it exists. Defaults to False.
        delete_on_success (bool): Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
        delete_on_failure (bool): Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
        tempdir (Optional[str]): Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        str: A temporary directory
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


def read_or_create_batch(folder, batch=None):
    # type: (str, bool) -> str
    """Get batch or create it if it doesn't exist

    Args:
        folder (str): Folder in which to look for or create batch file.
        batch (Optional[str]): Batch to use if there isn't one in a file already.

    Returns:
        str: Batch
    """
    batch_file = join(folder, 'batch.txt')
    if exists(batch_file):
        batch = load_file_to_str(batch_file, strip=True)
        logger.info('File BATCH = %s' % batch)
    else:
        if not batch:
            batch = get_uuid()
            logger.info('Generated BATCH = %s' % batch)
        save_str_to_file(batch, batch_file)
    return batch


@contextlib.contextmanager
def temp_dir_batch(folder=None, delete_if_exists=False, delete_on_success=True, delete_on_failure=True,
                   batch=None, tempdir=None):
    # type: (Optional[str], bool, bool, bool, Optional[str], Optional[str]) -> str
    """Get a temporary directory optionally with folder appended (and created if it doesn't exist)

    Args:
        folder (Optional[str]): Folder to create in temporary folder. Defaults to None.
        delete_if_exists (bool): Whether to delete the folder if it exists. Defaults to False.
        delete_on_success (bool): Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
        delete_on_failure (bool): Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.
        batch (Optional[str]): Batch to use if there isn't one in a file already.
        tempdir (Optional[str]): Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        str: A temporary directory
    """
    with temp_dir(folder, delete_if_exists, delete_on_success, delete_on_failure, tempdir=tempdir) as tempdir:
        yield {'folder': tempdir, 'batch': read_or_create_batch(tempdir, batch)}


def get_wheretostart(text, message, key):
    # type: (str, str, str) -> Optional[str]
    """Evaluate WHERETOSTART.

    Args:
        text (str): String to process
        message (str): Text for logging
        key (str): Key to comapre with

    Returns:
        Optional[str]: A string or None
    """
    upper_text = text.upper()
    if upper_text == 'RESET':
        return None
    w_key, wheretostart = text.split('=')
    if w_key == key:
        logger.info('%s WHERETOSTART = %s' % (message, wheretostart))
        return wheretostart
    else:
        return 'IGNORE'


def progress_storing_folder(info, iterator, key, wheretostart=None):
    # type: (Dict, Iterable[Dict], str, Optional[str]) -> Tuple[Dict,Dict]
    """Store progress in folder in key folder of info dictionary parameter. Yields 2 dictionaries. The first is the
    info dictionary. It contains in key folder the folder being used to store progress and in key progress the current
    position in the iterator. If store_batch is True, that dictionary will also contain the key batch containing a batch
    code to be passed as the batch parameter in create_in_hdx or update_in_hdx calls. The second dictionary is the next
    dictionary in the iterator.

    Args:
        info (Dict): Dictionary containing folder and anything else to be yielded
        iterator (Iterable[Dict]): Iterate over this object persisting progress
        key (str): Key to examine from dictionary from iterator
        wheretostart (Optional[str]): Where in iterator to start

    Returns:
        Tuple[Dict,Dict]: A tuple of the form (info dictionary, next object in iterator)
    """
    folder = info['folder']
    progress_file = join(folder, 'progress.txt')

    if not wheretostart:
        contents = getenv('WHERETOSTART')
        if contents:
            wheretostart = get_wheretostart(contents, 'Environment variable', key)
        else:
            if exists(progress_file):
                contents = load_file_to_str(progress_file, strip=True)
                wheretostart = get_wheretostart(contents, 'File', key)
            else:
                wheretostart = None
    found = False
    for nextdict in iterator:
        current = nextdict[key]
        if wheretostart:
            if wheretostart == 'IGNORE':
                continue
            if not found:
                if current == wheretostart:
                    found = True
                    logger.info('Starting run from WHERETOSTART %s' % wheretostart)
                else:
                    logger.info('Run not started. Ignoring %s. WHERETOSTART (%s) not matched.' % (current,
                                                                                                  wheretostart))
                    continue
        output = '%s=%s' % (key, current)
        info['progress'] = output
        save_str_to_file(output, progress_file)
        yield info, nextdict
    if wheretostart and not found:
        raise NotFoundError('WHERETOSTART (%s) not matched in iterator with key %s and no run started!' % (wheretostart, key))


def progress_storing_tempdir(folder, iterator, key, batch=None, tempdir=None):
    # type: (str, Iterable[Dict], str, Optional[str], Optional[str]) -> Tuple[Dict,Dict]
    """Store progress in temporary directory. The folder persists until the final iteration allowing which iteration to
    start at and the batch code to be persisted between runs. Yields 2 dictionaries. The first contains key folder which
    is the temporary directory optionally with folder appended (and created if it doesn't exist). In key progress is
    held the current position in the iterator. It also contains the key batch containing a batch code to be passed as
    the batch parameter in create_in_hdx or update_in_hdx calls. The second dictionary is the next dictionary in the
    iterator.

    Args:
        folder (str): Folder to create in temporary folder
        iterator (Iterable[Dict]): Iterate over the iterator persisting progress
        key (str): Key to examine from dictionary from iterator
        batch (Optional[str]): Batch to use if there isn't one in a file already.
        tempdir (Optional[str]): Folder to use as temporary directory. Defaults to None (TEMP_DIR or os.gettempdir).

    Returns:
        Tuple[Dict,Dict]: A tuple of the form (info dictionary, next object in iterator)
    """
    delete_if_exists = False
    wheretostart = getenv('WHERETOSTART')
    if wheretostart:
        if wheretostart.upper() == 'RESET':
            delete_if_exists = True
            logger.info('Removing progress file and will start from beginning!')
    with temp_dir_batch(folder, delete_if_exists, delete_on_success=True, delete_on_failure=False,
                        batch=batch, tempdir=tempdir) as info:
        for result in progress_storing_folder(info, iterator, key):
            yield result


def multiple_progress_storing_tempdir(folder, iterators, keys, batch=None):
    # type: (str, List[Iterable[Dict]], List[str], Optional[str]) -> Tuple[Dict,Dict]
    """Store progress in temporary directory. The folder persists until the final iteration of the last iterator
    allowing which iteration to start at and the batch code to be persisted between runs. Yields 2 dictionaries. The
    first contains key folder which is the temporary directory optionally with folder appended (and created if it
    doesn't exist). In key progress is held the current position in the iterator. It also contains the key batch
    containing a batch code to be passed as the batch parameter in create_in_hdx or update_in_hdx calls. The second
    dictionary is the next dictionary in the iterator.

    Args:
        folder (str): Folder to create in temporary folder
        iterators (List[Iterable[Dict]): Iterate over each iterator in the list consecutively persisting progress
        keys (List[str]): Key to examine from dictionary from each iterator in the above list
        batch (Optional[str]): Batch to use if there isn't one in a file already.

    Returns:
        Tuple[int, Dict,Dict]: A tuple of the form (iterator index, info dictionary, next object in iterator)
    """
    delete_if_exists = False
    wheretostartenv = getenv('WHERETOSTART')
    if wheretostartenv:
        if wheretostartenv.upper() == 'RESET':
            delete_if_exists = True
            logger.info('Removing progress file and will start from beginning!')
    with temp_dir_batch(folder, delete_if_exists, delete_on_success=True, delete_on_failure=False, batch=batch) as info:
        tempdir = info['folder']
        batch = info['batch']
        for i, key in enumerate(keys):
            progress_file = join(tempdir, 'progress.txt')
            if wheretostartenv:
                wheretostart = get_wheretostart(wheretostartenv, 'Environment variable', key)
            else:
                if exists(progress_file):
                    contents = load_file_to_str(progress_file, strip=True)
                    wheretostart = get_wheretostart(contents, 'File', key)
                else:
                    wheretostart = None
            with temp_dir_batch(str(i), False, delete_on_success=True, delete_on_failure=False,
                                batch=batch, tempdir=tempdir) as info:
                for info, nextdict in progress_storing_folder(info, iterators[i], key, wheretostart):
                    save_str_to_file(info['progress'], progress_file)
                    yield i, info, nextdict
                if exists(progress_file):
                    remove(progress_file)
