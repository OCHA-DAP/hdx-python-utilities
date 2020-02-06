# -*- coding: utf-8 -*-
"""Directory Path Utilities"""
import contextlib
import inspect
import logging
import sys
from os import getenv, makedirs
from os.path import abspath, realpath, dirname, join, exists
from shutil import rmtree
from tempfile import gettempdir
from typing import Any, Optional, Iterable, Tuple, Dict

from hdx.utilities.loader import load_file_to_str
from hdx.utilities.saver import save_str_to_file

logger = logging.getLogger(__name__)


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


def get_temp_dir():
    # type: () -> str
    """Get a temporary directory. Looks for environment variable TEMP_DIR and falls
    back on os.gettempdir.

    Returns:
        str: A temporary directory
    """
    return getenv('TEMP_DIR', gettempdir())


@contextlib.contextmanager
def temp_dir(folder=None, delete_on_success=True, delete_on_failure=True):
    # type: (Optional[str], bool, bool) -> str
    """Get a temporary directory optionally with folder appended (and created if it doesn't exist)

    Args:
        folder (Optional[str]): Folder to create in temporary folder. Defaults to None.
        delete_on_success (bool): Whether to delete folder (if folder supplied) on exiting with statement successfully. Defaults to True.
        delete_on_failure (bool): Whether to delete folder (if folder supplied) on exiting with statement unsuccessfully. Defaults to True.

    Returns:
        str: A temporary directory
    """
    tempdir = get_temp_dir()
    if folder:
        tempdir = join(tempdir, folder)
    if not exists(tempdir):
        makedirs(tempdir)
    try:
        yield tempdir
        if folder and delete_on_success:
            rmtree(tempdir)
    except:
        if folder and delete_on_failure:
            rmtree(tempdir)
        raise


def progress_storing_tempdir(folder, iterator, key):
    # type: (str, Iterable[Dict], str) -> Tuple[str,Dict]
    """Yield a temporary directory optionally with folder appended (and created if it doesn't exist)
    and the next dictionary in the iterator. The folder persists until the final iteration and which
    iteration to start at is persisted between runs.

    Args:
        folder (str): Folder to create in temporary folder
        iterator (Iterable[Dict]): Iterate over this object persisting progress
        key (str): Key to examine from dictionary from iterator

    Returns:
        Tuple[str,Dict]: A tuple of the form (temporary directory, next object in iterator)
    """
    with temp_dir(folder, delete_on_success=True, delete_on_failure=False) as tempdir:
        progress_file = join(tempdir, 'progress.txt')
        wheretostart = getenv('WHERETOSTART')
        if wheretostart:
            wheretostart = wheretostart.upper()
            if wheretostart == 'RESET':
                rmtree(tempdir)
                makedirs(tempdir)
                wheretostart = None
                logger.info('Removing progress file and will start from beginning!')
            else:
                logger.info('Environment variable WHERETOSTART = %s' % wheretostart)
        else:
            if exists(progress_file):
                wheretostart = load_file_to_str(progress_file, strip=True)
                logger.info('File WHERETOSTART = %s' % wheretostart)
        found = False
        for nextdict in iterator:
            currentlocation = nextdict[key]
            if wheretostart and not found:
                if currentlocation == wheretostart:
                    found = True
                    logger.info('Starting run from WHERETOSTART %s' % wheretostart)
                else:
                    logger.info('Run not started. Ignoring %s. WHERETOSTART (%s) not matched.' % (currentlocation,
                                                                                                  wheretostart))
                    continue
            save_str_to_file(currentlocation, progress_file)
            yield tempdir, nextdict
