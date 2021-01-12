# -*- coding: utf-8 -*-
"""Version utility"""
import logging

from hdx.utilities.loader import load_file_to_str
from hdx.utilities.path import script_dir_plus_file

logger = logging.getLogger(__name__)


def get_utils_version():
    return load_file_to_str(script_dir_plus_file('version.txt', get_utils_version), strip=True)
