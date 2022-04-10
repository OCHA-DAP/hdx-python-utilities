"""Saving utilities for YAML, JSON etc."""
import json
from collections import OrderedDict
from typing import Any

from ruamel.yaml import (
    YAML,
    RoundTripRepresenter,
    SafeRepresenter,
    add_representer,
)


class UnPrettyRTRepresenter(RoundTripRepresenter):
    def represent_none(self, data: Any) -> Any:
        return self.represent_scalar("tag:yaml.org,2002:null", "null")


class UnPrettySafeRepresenter(SafeRepresenter):
    def represent_none(self, data: Any) -> Any:
        return self.represent_scalar("tag:yaml.org,2002:null", "null")


class PrettySafeRepresenter(SafeRepresenter):
    def represent_none(self, data: Any) -> Any:
        if (
            len(self.represented_objects) == 0
            and not self.serializer.use_explicit_start
        ):
            # this will be open ended (although it is not yet)
            return self.represent_scalar("tag:yaml.org,2002:null", "null")
        return self.represent_scalar("tag:yaml.org,2002:null", "")


UnPrettyRTRepresenter.add_representer(
    None, UnPrettyRTRepresenter.represent_none
)
UnPrettySafeRepresenter.add_representer(
    None, UnPrettySafeRepresenter.represent_none
)
PrettySafeRepresenter.add_representer(
    None, PrettySafeRepresenter.represent_none
)


representers = {
    False: {False: UnPrettyRTRepresenter, True: RoundTripRepresenter},
    True: {False: UnPrettySafeRepresenter, True: PrettySafeRepresenter},
}


def save_text(string: str, path: str, encoding: str = "utf-8") -> None:
    """Save text string to file

    Args:
        string (str): String to save
        path (str): Path to file
        encoding (str): Encoding of file. Defaults to utf-8.

    Returns:
        None
    """
    with open(path, "w", encoding=encoding) as f:
        f.write(string)


def save_yaml(
    object: Any,
    path: str,
    encoding: str = "utf-8",
    pretty: bool = False,
    sortkeys: bool = False,
) -> None:
    """Save dictionary to YAML file preserving order if it is an OrderedDict

    Args:
        object (Any): Python object to save
        path (str): Path to YAML file
        encoding (str): Encoding of file. Defaults to utf-8.
        pretty (bool): Whether to pretty print. Defaults to False.
        sortkeys (bool): Whether to sort dictionary keys. Defaults to False.

    Returns:
        None
    """
    with open(path, "w", encoding=encoding) as f:
        representer = representers[sortkeys][pretty]
        yaml = YAML(typ="rt")
        yaml.Representer = representer
        add_representer(
            OrderedDict, representer.represent_dict, representer=representer
        )
        if pretty:
            yaml.indent(offset=2)
        else:
            yaml.default_flow_style = None
        yaml.representer.add_representer(
            type(None), representer.represent_none
        )
        yaml.dump(object, f)


def save_json(
    object: Any,
    path: str,
    encoding: str = "utf-8",
    pretty: bool = False,
    sortkeys: bool = False,
) -> None:
    """Save dictionary to JSON file preserving order if it is an OrderedDict

    Args:
        object (Any): Python object to save
        path (str): Path to JSON file
        encoding (str): Encoding of file. Defaults to utf-8.
        pretty (bool): Whether to pretty print. Defaults to False.
        sortkeys (bool): Whether to sort dictionary keys. Defaults to False.

    Returns:
        None
    """
    with open(path, "w", encoding=encoding) as f:
        if pretty:
            indent = 2
            separators = (",", ": ")
        else:
            indent = None
            separators = (", ", ": ")
        json.dump(
            object,
            f,
            indent=indent,
            sort_keys=sortkeys,
            separators=separators,
        )
