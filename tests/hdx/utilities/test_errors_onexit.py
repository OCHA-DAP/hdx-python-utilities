"""Errors on exit Tests"""
import logging

import pytest

from hdx.utilities.errors_onexit import ErrorsOnExit


class TestErrorsOnExit:
    def test_errorsonexit(self, caplog):
        with ErrorsOnExit() as errors:
            assert len(errors.errors) == 0
        with pytest.raises(SystemExit):
            with caplog.at_level(logging.ERROR):
                with ErrorsOnExit() as errors:
                    errors.add("error 1")
                    errors.add("error 2")
                    assert len(errors.errors) == 2
                assert "error 1" in caplog.text
                assert "error 2" in caplog.text
