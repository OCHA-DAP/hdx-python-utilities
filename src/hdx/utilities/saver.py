# -*- coding: utf-8 -*-
"""Saving utilities for YAML, JSON etc."""
import json
from io import StringIO
from collections import OrderedDict
from io import open
from typing import Dict

import six
from ruamel.yaml import YAML, RoundTripRepresenter, add_representer, SafeRepresenter


def represent_none(self, data):
    return self.represent_scalar('tag:yaml.org,2002:null', 'null')


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
    with open(path, 'w', encoding=encoding) as f:
        yaml = YAML(typ='rt')
        if sortkeys:
            add_representer(OrderedDict, SafeRepresenter.represent_dict, representer=SafeRepresenter)
            yaml.Representer = SafeRepresenter
        else:
            add_representer(OrderedDict, RoundTripRepresenter.represent_dict, representer=RoundTripRepresenter)
            yaml.Representer = RoundTripRepresenter
        if pretty:
            yaml.indent(offset=2)
            yaml.representer.add_representer(type(None), RoundTripRepresenter.represent_none)
        else:
            yaml.default_flow_style = None
            yaml.representer.add_representer(type(None), represent_none)
        yaml.dump(dictionary, f)


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
