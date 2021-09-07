"""Encoding Utility Tests"""
from hdx.utilities.encoding import base64_to_str, str_to_base64


class TestEncoding:
    def test_base64(self):
        string = "hello"
        result = str_to_base64(string)
        assert result == "aGVsbG8="
        assert base64_to_str(result) == string
