"""Loading utilities for YAML, JSON etc."""

import json
from typing import Any, Dict, Optional
from warnings import warn

from ruamel.yaml import YAML

from .dictandlist import merge_dictionaries, merge_two_dictionaries
from .typehint import ListTuple


class LoadError(Exception):
    pass


def load_text(
    path: str,
    encoding: str = "utf-8",
    strip: bool = False,
    replace_newlines: Optional[str] = None,
    replace_line_separators: Optional[str] = None,
    loaderror_if_empty: bool = True,
    default_line_separator: str = "\n",
) -> str:
    """Load file into a string removing newlines.

    Args:
        path (str): Path to file
        encoding (str): Encoding of file. Defaults to utf-8.
        strip (bool): Whether to strip whitespace from start and end. Defaults to False.
        replace_newlines (Optional[str]): String with which to replace newlines. Defaults to None (don't replace). (deprecated 2024-02-07)
        replace_line_separators (Optional[str]): String with which to replace newlines. Defaults to None (don't replace).
        loaderror_if_empty (bool): Whether to raise LoadError if file is empty. Default to True.
        default_line_separator (str): line separator to be replaced if replace_line_separators is not None

    Returns:
        str: String contents of file
    """
    if replace_newlines is not None:
        warn(
            "Keyword argument 'replace_newlines' to 'load_text' is deprecated on 2024-02-08 "
            "in favour of 'replace_line_separators'",
            DeprecationWarning,
            stacklevel=2,
        )
        replace_line_separators = replace_newlines
    with open(path, encoding=encoding) as f:
        string = f.read()
        if replace_line_separators is not None:
            string = string.replace(
                default_line_separator, replace_line_separators
            )
        if strip:
            string = string.strip()
    if not string:
        if loaderror_if_empty:
            raise LoadError(f"{path} file is empty!")
        return ""
    return string


def load_yaml(
    path: str, encoding: str = "utf-8", loaderror_if_empty: bool = True
) -> Any:
    """Load YAML file into an ordered dictionary.

    Args:
        path (str): Path to YAML file
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if file is empty. Default to True.

    Returns:
        Any: The data from the YAML file
    """
    with open(path, encoding=encoding) as f:
        yaml = YAML()
        yamlobj = yaml.load(f.read())
    if not yamlobj:
        if loaderror_if_empty:
            raise LoadError(f"YAML file: {path} is empty!")
        return None
    return yamlobj


def load_json(
    path: str, encoding: str = "utf-8", loaderror_if_empty: bool = True
) -> Any:
    """Load JSON file into an ordered dictionary (dict for Python 3.7+)

    Args:
        path (str): Path to JSON file
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if file is empty. Default to True.

    Returns:
        Any: The data from the JSON file
    """
    with open(path, encoding=encoding) as f:
        jsonobj = json.loads(f.read())
    if not jsonobj:
        if loaderror_if_empty:
            raise LoadError(f"JSON file: {path} is empty!")
        return None
    return jsonobj


def load_and_merge_yaml(
    paths: ListTuple[str],
    encoding: str = "utf-8",
    loaderror_if_empty: bool = True,
) -> Dict:
    """Load multiple YAML files that are in dictionary form and merge into one
    dictionary.

    Args:
        paths (ListTuple[str]): Paths to YAML files
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if any file is empty. Default to True.

    Returns:
        Dict: Dictionary of merged YAML files
    """
    configs = [
        load_yaml(
            path, encoding=encoding, loaderror_if_empty=loaderror_if_empty
        )
        for path in paths
    ]
    return merge_dictionaries(configs)


def load_and_merge_json(
    paths: ListTuple[str],
    encoding: str = "utf-8",
    loaderror_if_empty: bool = True,
) -> Dict:
    """Load multiple JSON files that are in dictionary form and merge into one
    dictionary.

    Args:
        paths (ListTuple[str]): Paths to JSON files
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if any file is empty. Default to True.

    Returns:
        Dict: Dictionary of merged JSON files
    """
    configs = [
        load_json(
            path, encoding=encoding, loaderror_if_empty=loaderror_if_empty
        )
        for path in paths
    ]
    return merge_dictionaries(configs)


def load_yaml_into_existing_dict(
    data: dict,
    path: str,
    encoding: str = "utf-8",
    loaderror_if_empty: bool = True,
) -> Dict:
    """Merge YAML file that is in dictionary form into existing dictionary.

    Args:
        data (dict): Dictionary to merge into
        path (str): YAML file to load and merge
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if file is empty. Default to True.

    Returns:
        Dict: YAML file merged into dictionary
    """
    yamldict = load_yaml(
        path, encoding=encoding, loaderror_if_empty=loaderror_if_empty
    )
    return merge_two_dictionaries(data, yamldict)


def load_json_into_existing_dict(
    data: dict,
    path: str,
    encoding: str = "utf-8",
    loaderror_if_empty: bool = True,
) -> Dict:
    """Merge JSON file that is in dictionary form into existing dictionary.

    Args:
        data (dict): Dictionary to merge into
        path (str): JSON file to load and merge
        encoding (str): Encoding of file. Defaults to utf-8.
        loaderror_if_empty (bool): Whether to raise LoadError if file is empty. Default to True.

    Returns:
        dict: JSON file merged into dictionary
    """
    jsondict = load_json(
        path, encoding=encoding, loaderror_if_empty=loaderror_if_empty
    )
    return merge_two_dictionaries(data, jsondict)
