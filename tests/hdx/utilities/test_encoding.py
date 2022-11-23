"""Encoding Utility Tests"""
from hdx.utilities.encoding import (
    base64_to_str,
    basicauth_decode,
    basicauth_encode,
    str_to_base64,
)


class TestEncoding:
    def test_base64(self):
        string = "hello"
        result = str_to_base64(string)
        assert result == "aGVsbG8="
        assert base64_to_str(result) == string

    def test_basicauth(self):
        user = "user"
        password = "password"
        result = basicauth_encode(user, password)
        assert result == "Basic dXNlcjpwYXNzd29yZA=="
        result = basicauth_decode(result)
        assert result == (user, password)
