"""Errors on exit Tests"""
import logging

import pytest

from hdx.utilities.easy_logging import setup_logging
from hdx.utilities.errors_onexit import ErrorsOnExit

setup_logging()


class TestErrorsOnExit:
    def test_errorsonexit(self, caplog):
        with ErrorsOnExit() as errors:
            assert len(errors.errors) == 0
        with pytest.raises(SystemExit):
            with caplog.at_level(logging.ERROR):
                with ErrorsOnExit():
                    logging.errors_on_exit.add("error 1")
                    logging.errors_on_exit.add("error 2")
                    assert len(logging.errors_on_exit.errors) == 2
                assert "error 1" in caplog.text
                assert "error 2" in caplog.text
