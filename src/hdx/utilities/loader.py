"""Loading utilities for YAML, JSON etc."""

import json
from os import linesep
from typing import Dict, List, Optional

from ruamel.yaml import YAML

from hdx.utilities.dictandlist import (
    merge_dictionaries,
    merge_two_dictionaries,
)


class LoadError(Exception):
    pass


def load_file_to_str(
    path: str,
    encoding: str = "utf-8",
    strip: bool = False,
    replace_newlines: Optional[str] = None,
) -> str:
    """
    Load file into a string removing newlines

    Args:
        path (str): Path to file
        encoding (str): Encoding of file. Defaults to utf-8.
        strip (bool): Whether to strip whitespace from start and end. Defaults to False.
        replace_newlines (Optional[str]): String with which tp replace newlines. Defaults to None (don't replace).

    Returns:
        str: String contents of file

    """
    with open(path, encoding=encoding) as f:
        string = f.read()
        if replace_newlines is not None:
            string = string.replace(linesep, replace_newlines)
        if strip:
            string = string.strip()
    if not string:
        raise LoadError(f"{path} file is empty!")
    return string


def load_yaml(path: str, encoding: str = "utf-8") -> Dict:
    """Load YAML file into an ordered dictionary

    Args:
        path (str): Path to YAML file
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        Dict: Ordered dictionary containing loaded YAML file
    """
    with open(path, encoding=encoding) as f:
        yaml = YAML()
        yamldict = yaml.load(f.read())
    if not yamldict:
        raise (LoadError(f"YAML file: {path} is empty!"))
    return yamldict


def load_json(path: str, encoding: str = "utf-8") -> Dict:
    """Load JSON file into an ordered dictionary (dict for Python 3.7+)

    Args:
        path (str): Path to JSON file
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        Dict: Ordered dictionary containing loaded JSON file
    """
    with open(path, encoding=encoding) as f:
        jsondict = json.loads(f.read())
    if not jsondict:
        raise (LoadError(f"JSON file: {path} is empty!"))
    return jsondict


def load_and_merge_yaml(paths: List[str], encoding: str = "utf-8") -> Dict:
    """Load multiple YAML files and merge into one dictionary

    Args:
        paths (List[str]): Paths to YAML files
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        Dict: Dictionary of merged YAML files

    """
    configs = [load_yaml(path, encoding=encoding) for path in paths]
    return merge_dictionaries(configs)


def load_and_merge_json(paths: List[str], encoding: str = "utf-8") -> Dict:
    """Load multiple JSON files and merge into one dictionary

    Args:
        paths (List[str]): Paths to JSON files
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        Dict: Dictionary of merged JSON files

    """
    configs = [load_json(path, encoding=encoding) for path in paths]
    return merge_dictionaries(configs)


def load_yaml_into_existing_dict(
    data: dict, path: str, encoding: str = "utf-8"
) -> Dict:
    """Merge YAML file into existing dictionary

    Args:
        data (dict): Dictionary to merge into
        path (str): YAML file to load and merge
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        Dict: YAML file merged into dictionary
    """
    yamldict = load_yaml(path, encoding=encoding)
    return merge_two_dictionaries(data, yamldict)


def load_json_into_existing_dict(
    data: dict, path: str, encoding: str = "utf-8"
) -> Dict:
    """Merge JSON file into existing dictionary

    Args:
        data (dict): Dictionary to merge into
        path (str): JSON file to load and merge
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        dict: JSON file merged into dictionary
    """
    jsondict = load_json(path, encoding=encoding)
    return merge_two_dictionaries(data, jsondict)
