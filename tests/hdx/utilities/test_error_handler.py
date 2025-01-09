"""Errors on exit Tests"""

import logging

import pytest

from hdx.utilities.easy_logging import setup_logging
from hdx.utilities.error_handler import ErrorHandler

setup_logging()


class TestErrorsHandler:
    def test_error_handler(self, caplog):
        with ErrorHandler() as errors:
            assert len(errors.shared_errors["warning"]) == 0
            assert len(errors.shared_errors["error"]) == 0
        with pytest.raises(SystemExit):
            with caplog.at_level(logging.ERROR):
                with ErrorHandler() as errors:
                    errors.add_message(
                        "this is a warning!", "warning 1", "warning"
                    )
                    errors.add_missing_value_message(
                        "this is a missing value error!",
                        "problem value",
                        "error 1",
                        "error",
                    )
                    errors.add_multi_valued_message(
                        "this is a multi valued warning!",
                        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
                        "warning 2",
                        "warning",
                    )
                    assert len(errors.shared_errors["warning"]) == 2
                    assert len(errors.shared_errors["error"]) == 1
                assert "missing value" in caplog.text
                assert "warning" not in caplog.text
                assert "multi" not in caplog.text
