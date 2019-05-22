# -*- coding: utf-8 -*-
"""Directory Path Utilities"""
import contextlib
import inspect
import sys
from os import getenv, makedirs
from os.path import abspath, realpath, dirname, join, exists
from shutil import rmtree
from tempfile import gettempdir
from typing import Any, Optional


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
    back on os.ggettempdir.

    Returns:
        str: A temporary directory
    """
    return getenv('TEMP_DIR', gettempdir())


@contextlib.contextmanager
def temp_dir(folder=None, delete=True):
    # type: (Optional[str], bool) -> str
    """Get a temporary directory optionally with folder appended (and created if it doesn't exist)

    Args:
        folder (Optional[str]): Folder to create in temporary folder. Defaults to None.
        delete (bool): Whether to delete folder (assuming folder arg supplied) on exiting with statement

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
    finally:
        if folder and delete:
            rmtree(tempdir)
