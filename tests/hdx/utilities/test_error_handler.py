"""Errors on exit Tests"""

import logging

import pytest

from hdx.utilities.easy_logging import setup_logging
from hdx.utilities.error_handler import ErrorHandler

setup_logging()


class TestErrorHandler:
    def test_error_handler(self, caplog):
        with ErrorHandler() as errors:
            assert len(errors.shared_errors["warning"]) == 0
            assert len(errors.shared_errors["error"]) == 0
        with pytest.raises(SystemExit):
            with caplog.at_level(logging.ERROR):
                with ErrorHandler(should_exit_on_error=True) as errors:
                    errors.add("this is a error!")
                    errors.add("this is a warning!", "warning 1", "warning")
                    errors.add_missing_value(
                        "this is a missing value error!",
                        "problem value",
                        "error 1",
                        "error",
                    )
                    errors.add_multi_valued(
                        "this is a multi valued warning!",
                        (1, 2, 3, 4),
                        "warning 1",
                        "warning",
                    )
                    errors.add_multi_valued(
                        "this is a multi valued error!",
                        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
                        "error 1",
                        "error",
                    )
                    errors.add_multi_valued(
                        "this is another multi valued warning!",
                        (),
                        "warning 1",
                        "warning",
                    )
                    assert len(errors.shared_errors["warning"]) == 1
                    assert len(errors.shared_errors["warning"]["warning 1"]) == 2
                    assert len(errors.shared_errors["error"]) == 2
                    assert len(errors.shared_errors["error"][""]) == 1
                    assert len(errors.shared_errors["error"]["error 1"]) == 2
                assert "missing value" in caplog.text
                assert "warning" not in caplog.text
                assert "multi" not in caplog.text
