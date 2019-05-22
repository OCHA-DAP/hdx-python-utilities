# -*- coding: utf-8 -*-
"""Saving utilities for YAML, JSON etc."""
import json
from io import open
from typing import Dict

import pyaml
import six
import yaml
import yamlloader


def save_str_to_file(string, path, encoding='utf-8'):
    # type: (str, str, str) -> None
    """Save string to file

    Args:
        string (str): String to save
        path (str): Path to file
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        None
    """
    with open(path, 'w', encoding=encoding) as f:
        if six.PY2:
            string = unicode(string)
        f.write(string)


def save_yaml(dictionary, path, encoding='utf-8', pretty=False, sortkeys=False):
    # type: (Dict, str, str, bool, bool) -> None
    """Save dictionary to YAML file preserving order if it is an OrderedDict

    Args:
        dictionary (Dict): Python dictionary to save
        path (str): Path to YAML file
        encoding (str): Encoding of file. Defaults to utf-8.
        pretty (bool): Whether to pretty print. Defaults to False.
        sortkeys (bool): Whether to sort dictionary keys. Defaults to False.

    Returns:
        None
    """
    if sortkeys:
        dictionary = dict(dictionary)
    with open(path, 'w', encoding=encoding) as f:
        if pretty:
            pyaml.dump(dictionary, f)
        else:
            yaml.dump(dictionary, f, default_flow_style=None, Dumper=yamlloader.ordereddict.CDumper)


def save_json(dictionary, path, encoding='utf-8', pretty=False, sortkeys=False):
    # type: (Dict, str, str, bool, bool) -> None
    """Save dictionary to JSON file preserving order if it is an OrderedDict

    Args:
        dictionary (Dict): Python dictionary to save
        path (str): Path to JSON file
        encoding (str): Encoding of file. Defaults to utf-8.
        pretty (bool): Whether to pretty print. Defaults to False.
        sortkeys (bool): Whether to sort dictionary keys. Defaults to False.

    Returns:
        None
    """
    with open(path, 'w', encoding=encoding) as f:
        if pretty:
            indent = 2
            separators = (',', ': ')
        else:
            indent = None
            separators = (', ', ': ')
        if six.PY3:
            json.dump(dictionary, f, indent=indent, sort_keys=sortkeys, separators=separators)
        else:
            string = json.dumps(dictionary, ensure_ascii=False, indent=indent,
                                sort_keys=sortkeys, separators=separators)
            f.write(unicode(string))
