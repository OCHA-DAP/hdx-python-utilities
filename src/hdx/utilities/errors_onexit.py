"""Collect and log errors on exit."""

import warnings

from hdx.utilities.error_handler import ErrorHandler


class ErrorsOnExit(ErrorHandler):  # pragma: no cover
    def __init__(self) -> None:
        warnings.warn(
            "The ErrorsOnExit class was renamed ErrorHandler and will be removed in future!",
            DeprecationWarning,
        )
        super().__init__()
