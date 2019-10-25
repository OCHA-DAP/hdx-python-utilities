# -*- coding: UTF-8 -*-
"""Encoding Utility Tests"""
from hdx.utilities.encoding import str_to_base64, base64_to_str


class TestEncoding:
    def test_base64(self):
        string = 'hello'
        result = str_to_base64(string)
        assert result == 'aGVsbG8='
        assert base64_to_str(result) == string
