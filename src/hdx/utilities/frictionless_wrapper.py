from typing import Any, Optional

import frictionless
import requests
from frictionless import FrictionlessException
from frictionless.errors import ResourceError
from frictionless.plugins.csv import CsvDialect
from frictionless.plugins.excel import ExcelDialect


def get_frictionless_resource(
    url: Optional[str] = None,
    ignore_blank_rows: bool = True,
    infer_types: bool = False,
    session: Optional[requests.Session] = None,
    data: Optional[Any] = None,
    **kwargs: Any,
) -> frictionless.Resource:
    """Get Frictionless Resource. Either url or data must be supplied.

    Args:
        url (Optional[str]): URL or path to download. Defaults to None.
        ignore_blank_rows (bool): Whether to ignore blank rows. Defaults to True.
        infer_types (bool): Whether to infer types. Defaults to False (strings).
        session (Optional[requests.Session]): Session to use. Defaults to not setting a session.
        data (Optional[Any]): Data to parse. Defaults to None.
        **kwargs:
        has_header (bool): Whether data has a header. Defaults to True.
        headers (Union[int, ListTuple[int], ListTuple[str]]): Number of row(s) containing headers or list of headers
        columns (Union[ListTuple[int], ListTuple[str], None]): Columns to pick. Defaults to all.
        file_type (Optional[str]): Type of file. Defaults to inferring.
        format (Optional[str]): Type of file. Defaults to inferring.
        encoding (Optional[str]): Type of encoding. Defaults to inferring.
        compression (Optional[str]): Type of compression. Defaults to inferring.
        delimiter (Optional[str]): Delimiter for values in csv rows. Defaults to inferring.
        skip_initial_space (bool): Ignore whitespace straight after delimiter. Defaults to False.
        sheet (Optional[Union[int, str]): Sheet in Excel. Defaults to inferring.
        fill_merged_cells (bool): Whether to fill merged cells. Defaults to True.
        http_session (Session): Session object to use. Defaults to downloader session.
        default_type (Optional[str]): Default field type if infer_types False. Defaults to any.
        float_numbers (bool): Use float not Decimal if infer_types True. Defaults to True.
        null_values (List[Any]): Values that will return None. Defaults to [""].
        dialect (Dialect): This can be set to override the above. See Frictionless docs.
        detector (Detector): This can be set to override the above. See Frictionless docs.
        layout (Layout): This can be set to override the above. See Frictionless docs.
        schema (Schema): This can be set to override the above. See Frictionless docs.

    Returns:
        frictionless.Resource: frictionless Resource object

    """
    if not url and not data:
        error = ResourceError(note="Neither url or data supplied!")
        raise FrictionlessException(error=error)
    file_type = kwargs.pop("file_type", None)
    format = kwargs.get("format", file_type)
    dialect = kwargs.get("dialect")
    if format is not None:
        kwargs["format"] = format
        if dialect is None:
            if format == "csv":
                dialect = CsvDialect()
                delimiter = kwargs.pop("delimiter", None)
                if delimiter is not None:
                    dialect.delimiter = delimiter
                skip_initial_space = kwargs.pop("skip_initial_space", None)
                if skip_initial_space is not None:
                    dialect.skip_initial_space = skip_initial_space
            elif format in ("xls", "xlsx"):
                dialect = ExcelDialect()
                sheet = kwargs.pop("sheet", None)
                if sheet is not None:
                    dialect.sheet = sheet
                fill_merged_cells = kwargs.pop("fill_merged_cells", True)
                dialect.fill_merged_cells = fill_merged_cells
    detector = kwargs.get("detector", frictionless.Detector())
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
    layout = kwargs.get("layout", frictionless.Layout())
    has_header = kwargs.pop("has_header", None)
    headers = kwargs.pop("headers", None)
    if headers is not None:
        if isinstance(headers, int):
            headers = [headers]
        if isinstance(headers[0], int):
            layout.header_rows = headers
        else:
            detector._Detector__field_names = headers
            if has_header is None:
                has_header = False
    if has_header is None:
        has_header = True
    layout.header = has_header
    columns = kwargs.pop("columns", None)
    if columns:
        layout.pick_fields = columns
    if ignore_blank_rows:
        if layout.skip_rows is None:
            layout.skip_rows = ["<blank>"]
        elif "<blank>" not in layout.skip_rows:
            layout.skip_rows.append("<blank>")
    kwargs["dialect"] = dialect
    kwargs["detector"] = detector
    kwargs["layout"] = layout
    http_session = kwargs.pop("http_session", session)
    if http_session is not None:
        frictionless.system.use_http_session(http_session)
    if url:
        resource = frictionless.Resource(path=url, **kwargs)
    else:
        resource = frictionless.Resource(data=data, **kwargs)
    resource.open()
    return resource
