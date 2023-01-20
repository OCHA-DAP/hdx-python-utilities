"""Frictionless wrapper"""
from typing import Any, Optional, Tuple

import requests
from frictionless import (
    Control,
    Detector,
    Dialect,
    FrictionlessException,
    Resource,
    system,
)
from frictionless.errors import ResourceError
from frictionless.formats import CsvControl, ExcelControl, JsonControl


def get_frictionless_control(**kwargs: Any) -> Tuple[Control, Any]:
    """Get Frictionless Control.

    Args:
        **kwargs:
        file_type (Optional[str]): Type of file. Defaults to inferring.
        format (Optional[str]): Type of file. Defaults to inferring.
        delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
        skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
        sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
        fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
        keyed (bool): Whether JSON is keyed. Defaults to True.
        keys (Optional[List[str]]): JSON keys to get. Defaults to None (all of them).
        property (Optional[str]): Path to table in JSON. Defaults to None.
        control (Control): This can be set to override the above. See Frictionless docs.

    Returns:
        Tuple[Control, Any]: (frictionless Control object, kwargs)
    """
    control = kwargs.get("control")
    file_type = kwargs.pop("file_type", None)
    file_format = kwargs.get("format", file_type)
    if file_format is not None:
        kwargs["format"] = file_format
        if control is None:
            if file_format == "csv":
                control = CsvControl()
                delimiter = kwargs.pop("delimiter", None)
                if delimiter is not None:
                    control.delimiter = delimiter
                skip_initial_space = kwargs.pop("skip_initial_space", None)
                if skip_initial_space is not None:
                    control.skip_initial_space = skip_initial_space
            elif file_format in ("xls", "xlsx"):
                control = ExcelControl()
                sheet = kwargs.pop("sheet", None)
                if sheet is not None:
                    control.sheet = sheet
                fill_merged_cells = kwargs.pop("fill_merged_cells", True)
                control.fill_merged_cells = fill_merged_cells
            elif file_format == "json":
                control = JsonControl()
                keyed = kwargs.pop("keyed", True)
                control.keyed = keyed
                keys = kwargs.pop("keys", None)
                if keys is not None:
                    control.keys = keys
                property = kwargs.pop("property", None)
                if property is not None:
                    control.property = property
                kwargs["type"] = "table"
    return control, kwargs


def get_frictionless_detector(
    infer_types: bool, **kwargs: Any
) -> Tuple[Detector, Any]:
    """Get Frictionless Detector.

    Args:
        infer_types (bool): Whether to infer types. Defaults to False (strings).
        **kwargs:
        default_type (Optional[str]): Default field type if infer_types False. Defaults to any.
        float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
        null_values (List[Any]): Values that will return None. Defaults to [""].
        detector (Detector): This can be set to override the above. See Frictionless docs.

    Returns:
        Tuple[Detector, Any]: (frictionless Detector object, kwargs)
    """
    detector = kwargs.get("detector", Detector())
    if infer_types:
        default = None
    else:
        default = "any"
    default_type = kwargs.pop("default_type", default)
    detector.field_type = default_type
    float_numbers = kwargs.pop("float_numbers", True)
    detector.field_float_numbers = float_numbers
    null_values = kwargs.pop("null_values", [""])
    detector.field_missing_values = null_values
    return detector, kwargs


def get_frictionless_dialect(
    ignore_blank_rows: bool, **kwargs: Any
) -> Tuple[Dialect, Any]:
    """Get Frictionless Dialect.

    Args:
        ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
        **kwargs:
        columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
        dialect (Dialect): This can be set to override the above. See Frictionless docs.

    Returns:
        Tuple[Dialect, Any]: (frictionless Dialect object, Any)
    """
    dialect = kwargs.get("dialect", Dialect())
    columns = kwargs.pop("columns", None)
    if columns:
        dialect.pick_fields = columns
    dialect.skip_blank_rows = ignore_blank_rows
    return dialect, kwargs


def get_frictionless_resource(
    url: Optional[str] = None,
    ignore_blank_rows: bool = True,
    infer_types: bool = False,
    session: Optional[requests.Session] = None,
    data: Optional[Any] = None,
    **kwargs: Any,
) -> Resource:
    """Get Frictionless Resource. Either url or data must be supplied.

    Args:
        url (Optional[str]): URL or path to download. Defaults to None.
        ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
        infer_types (bool): Whether to infer types. Defaults to False (strings).
        session (Optional[requests.Session]): Session to use. Defaults to not setting a session.
        data (Optional[Any]): Data to parse. Defaults to None.
        **kwargs:
        has_header (bool): Whether data has a header. Defaults to True.
        headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers.  # pylint: disable=line-too-long
        columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
        file_type (Optional[str]): Type of file. Defaults to inferring.
        format (Optional[str]): Type of file. Defaults to inferring.
        encoding (Optional[str]): Type of encoding. Defaults to inferring.
        compression (Optional[str]): Type of compression. Defaults to inferring.
        delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
        skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
        sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
        fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
        keyed (bool): Whether JSON is keyed. Defaults to True.
        keys (Optional[List[str]]): JSON keys to get. Defaults to None (all of them).
        property (Optional[str]): Path to table in JSON. Defaults to None.
        http_session (Session): Session object to use. Defaults to downloader session.
        default_type (Optional[str]): Default field type if infer_types False. Defaults to any.
        float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
        null_values (List[Any]): Values that will return None. Defaults to [""].
        control (Control): This can be set to override the above. See Frictionless docs.
        detector (Detector): This can be set to override the above. See Frictionless docs.
        dialect (Dialect): This can be set to override the above. See Frictionless docs.
        schema (Schema): This can be set to override the above. See Frictionless docs.

    Returns:
        Resource: frictionless Resource object
    """
    if not url and not data:
        error = ResourceError(note="Neither url or data supplied!")
        raise FrictionlessException(error=error)
    control, kwargs = get_frictionless_control(**kwargs)
    detector, kwargs = get_frictionless_detector(infer_types, **kwargs)
    dialect, kwargs = get_frictionless_dialect(ignore_blank_rows, **kwargs)
    has_header = kwargs.pop("has_header", None)
    headers = kwargs.pop("headers", None)
    if headers is not None:
        if isinstance(headers, int):
            headers = [headers]
        if isinstance(headers[0], int):
            dialect.header_rows = headers
        else:
            detector.field_names = headers
            if has_header is None:
                has_header = False
    if has_header is None:
        has_header = True
    dialect.header = has_header
    kwargs["detector"] = detector
    kwargs["dialect"] = dialect
    if control:
        dialect.add_control(control)
    http_session = kwargs.pop("http_session", session)
    with system.use_context(http_session=http_session):
        if url:
            resource = Resource(path=url, **kwargs)
        else:
            resource = Resource(data=data, **kwargs)
        resource.open()
        return resource
