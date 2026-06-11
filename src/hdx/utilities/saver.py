"""Saving utilities for YAML, JSON etc."""

import json
from collections import OrderedDict
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ruamel.yaml import (
    YAML,
    RoundTripRepresenter,
    SafeRepresenter,
    add_representer,
)

from hdx.utilities.frictionless_wrapper import get_frictionless_tableresource


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


UnPrettyRTRepresenter.add_representer(None, UnPrettyRTRepresenter.represent_none)
UnPrettySafeRepresenter.add_representer(None, UnPrettySafeRepresenter.represent_none)
PrettySafeRepresenter.add_representer(None, PrettySafeRepresenter.represent_none)


representers = {
    False: {False: UnPrettyRTRepresenter, True: RoundTripRepresenter},
    True: {False: UnPrettySafeRepresenter, True: PrettySafeRepresenter},
}


def save_text(string: str, path: Path | str, encoding: str = "utf-8") -> None:
    """Save text string to file.

    Args:
        string: String to save
        path: Path to file
        encoding: Encoding of file. Defaults to utf-8.

    Returns:
        None
    """
    with open(path, "w", encoding=encoding) as f:
        f.write(string)


def save_yaml(
    object: Any,
    path: Path | str,
    encoding: str = "utf-8",
    pretty: bool = False,
    sortkeys: bool = False,
) -> None:
    """Save dictionary to YAML file preserving order if it is an OrderedDict.

    Args:
        object: Python object to save
        path: Path to YAML file
        encoding: Encoding of file. Defaults to utf-8.
        pretty: Whether to pretty print. Defaults to False.
        sortkeys: Whether to sort dictionary keys. Defaults to False.

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
        yaml.representer.add_representer(type(None), representer.represent_none)
        yaml.dump(object, f)


def save_json(
    object: Any,
    path: Path | str,
    encoding: str = "utf-8",
    pretty: bool = False,
    sortkeys: bool = False,
) -> None:
    """Save dictionary to JSON file preserving order if it is an OrderedDict.

    Args:
        object: Python object to save
        path: Path to JSON file
        encoding: Encoding of file. Defaults to utf-8.
        pretty: Whether to pretty print. Defaults to False.
        sortkeys: Whether to sort dictionary keys. Defaults to False.

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


def save_iterable(
    filepath: Path | str,
    rows: Iterable[Sequence | Mapping],
    headers: int | Sequence[str] | None = None,
    columns: Sequence[int] | Sequence[str] | None = None,
    format: str = "csv",
    encoding: str | None = None,
    row_function: Callable[[dict], dict | None] | None = None,
    no_empty: bool = True,
) -> list:
    """Save an iterable of rows in dict or list form to a csv. The headers
    argument is either a row number (rows start counting at 1), or the actual
    headers defined as a list of strings, the order of which defines the column order.
    Columns not named in that list of strings will be dropped. If headers is not set,
    all rows will be treated as containing values. The columns argument defines which
    columns will be output. It can be used in conjunction with an integer headers with
    columns selecting the columns and hedders selecting the starting row.

    Args:
        filepath: Path to write to
        rows: List of rows in dict or list form
        headers: Headers to write. Defaults to None.
        columns: Columns to write. Defaults to all.
        format: Format to write. Defaults to csv.
        encoding: Encoding to use. Defaults to None (infer encoding).
        row_function: Row function to call for each row. Defaults to None.
        no_empty: Don't save file if there are no data rows. Defaults to True.

    Returns:
        List of rows written to file
    """
    if row_function is None:

        def row_function(row):
            return row

    def write_rows(newrows, has_header, headers) -> None:
        resource = get_frictionless_tableresource(
            data=newrows,
            has_header=has_header,
            headers=headers,
            encoding=encoding,
        )
        resource.write(filepath, format=format, encoding=encoding)
        resource.close()

    newrows = []
    rows = iter(rows)
    try:
        row = next(rows)
    except StopIteration:
        if not no_empty and headers:
            newrows = [headers]
            write_rows(newrows, None, None)
        return newrows

    if isinstance(row, dict):
        has_header = True
        row = row_function(row)
        try:
            while row is None:
                row = next(rows)
                row = row_function(row)
        except StopIteration:
            if not no_empty and headers:
                newrows = [headers]
                write_rows(newrows, None, None)
            return newrows
        if columns:
            row = {k: row[k] for k in columns if k in row}
            newrows.append(row)
            if headers is None:
                headers = columns
        else:
            if headers and isinstance(headers, list):
                row = {k: row.get(k) for k in headers}
            newrows.append(row)
        for row in rows:
            row = row_function(row)
            if row is None:
                continue
            newrows.append(row)
    else:
        if headers is None:
            headers = 1
        if isinstance(headers, int):
            headers_rowno = headers
            headers = row
            for i in range(headers_rowno - 1):
                headers = next(rows)
        else:
            headers_rowno = None
        has_header = False
        row = row_function(row)
        if columns:
            if headers_rowno is None and row is not None:
                newrow = []
                for column in columns:
                    newrow.append(row[column - 1])
                newrows.append(newrow)
            for row in rows:
                row = row_function(row)
                if row is None:
                    continue
                newrow = []
                for column in columns:
                    newrow.append(row[column - 1])
                newrows.append(newrow)
        else:
            if headers_rowno is None and row is not None:
                newrows.append(row)
            for row in rows:
                row = row_function(row)
                if row is None:
                    continue
                newrows.append(row)
    write_rows(newrows, has_header, headers)
    return newrows
