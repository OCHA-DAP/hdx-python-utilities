"""Saving utilities for YAML, JSON etc."""
import csv
import json
from collections import OrderedDict
from os.path import join
from typing import Any, Dict

from ruamel.yaml import (
    YAML,
    RoundTripRepresenter,
    SafeRepresenter,
    add_representer,
)

from .text import match_template_variables
from .typehint import ListTuple, ListTupleDict


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
    """Save text string to file.

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
    """Save dictionary to YAML file preserving order if it is an OrderedDict.

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
    """Save dictionary to JSON file preserving order if it is an OrderedDict.

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


def save_hxlated_output(
    configuration: Dict,
    rows: ListTuple[ListTupleDict],
    includes_header: bool = True,
    includes_hxltags: bool = False,
    output_dir: str = "",
    **kwargs: Any,
) -> None:
    """Save rows with header and HXL hashtags. Currently, JSON and/or csv
    outputs are supported. An output directory (which defaults to "") can be
    given. The utility expects a configuration containing definitions of input
    headers and HXLtags if these are not included in the rows, and output files
    with desired HXL hashtags. Keyword arguments are used to pass in any
    variables needed by the metadata defined in the configuration.

    Args:
        configuration (Dict): Configuration for input and output
        rows (ListTuple[ListTupleDict]): Rows of data
        includes_header (bool): Whether rows includes header. Defaults to True,
        includes_hxltags (bool): Whether rows includes HXL hashtags. Defaults to False.
        output_dir (str): Output directory. Defaults to "".
        **kwargs: Variables to use when evaluating template arguments

    Returns:
        None
    """
    row0 = rows[0]
    if includes_header:
        if isinstance(row0, dict):
            headers = list(row0.keys())
        else:
            headers = rows[0]
            rows = rows[1:]
    else:
        headers = configuration["input"]["headers"]
    if includes_hxltags:
        if isinstance(row0, dict):
            hxltags = list(row0.values())
            rows = rows[1:]
        else:
            hxltags = rows[0]
            rows = rows[1:]
    else:
        hxltags = configuration["input"]["hxltags"]
    expressions = {}
    for process in configuration.get("process", []):
        headers.append(process["header"])
        hxltag = process["hxltag"]
        hxltags.append(hxltag)
        expressions[hxltag] = process["expression"]

    hxltag_to_header = dict(zip(hxltags, headers))
    csv_configuration = configuration["output"].get("csv")
    if csv_configuration:
        csv_hxltags = csv_configuration.get("hxltags", hxltags)
        csv_headers = [hxltag_to_header[hxltag] for hxltag in csv_hxltags]
        csv_file = open(
            join(output_dir, csv_configuration["filename"]),
            "w",
            encoding="utf-8",
            newline="\n",
        )
        output_csv = csv.writer(csv_file)
        output_csv.writerow(csv_headers)
        output_csv.writerow(csv_hxltags)
    else:
        csv_file = None
        output_csv = None
    json_configuration = configuration["output"].get("json")
    if json_configuration:
        data_key = json_configuration.get("data")
        json_hxltags = json_configuration.get("hxltags", hxltags)
        metadata_configuration = json_configuration.get("metadata")
        if metadata_configuration:
            metadata = {}
            for metadata_name, value in metadata_configuration.items():
                if isinstance(value, str):
                    template_string, match_string = match_template_variables(
                        value
                    )
                    if template_string:
                        value = kwargs.get(match_string)
                if value is None:
                    continue
                metadata[metadata_name] = value
            metadata_json = json.dumps(
                metadata, indent=None, separators=(",", ":")
            )
        else:
            metadata_json = None

        output_json = open(
            join(output_dir, json_configuration["filename"]), "w"
        )

        if metadata_json:
            metadata_key = metadata_configuration.get("key", "metadata")
            if data_key is None:
                data_key = "data"
            output_string = (
                f'{{"{metadata_key}":{metadata_json},"{data_key}":[\n'
            )
        elif data_key is None:
            output_string = "[\n"
        else:
            output_string = f'{{"{data_key}":[\n'
        output_json.write(output_string)
    else:
        output_json = None
        data_key = None

    def write_row(inrow, ending):
        if isinstance(inrow, dict):
            inrow = list(inrow.values())

        def get_outrow(file_hxltags):
            outrow = {}
            for file_hxltag in file_hxltags:
                expression = expressions.get(file_hxltag)
                if expression:
                    for i, hxltag in enumerate(hxltags):
                        expression = expression.replace(hxltag, f"inrow[{i}]")
                    outrow[file_hxltag] = eval(expression)
                else:
                    outrow[file_hxltag] = inrow[hxltags.index(file_hxltag)]
            return outrow

        if output_csv:
            output_csv.writerow(get_outrow(csv_hxltags).values())
        if output_json:
            row = get_outrow(json_hxltags)
            output_json.write(
                json.dumps(row, indent=None, separators=(",", ":")) + ending
            )

    [write_row(row, ",\n") for row in rows[:-1]]
    write_row(rows[-1], "\n]")
    if output_json:
        if data_key is not None:
            output_json.write("}")
        output_json.close()
    if csv_file:
        csv_file.close()
