"""Encoding utilities."""

import base64
from urllib.parse import quote, unquote


def str_to_base64(string: str) -> str:
    """Base 64 encode string.

    Args:
        string: String to encode

    Returns:
        Base 64 encoded string
    """
    return base64.urlsafe_b64encode(string.encode("utf-8")).decode("utf-8")


def base64_to_str(bstring: str) -> str:
    """Base 64 decode string.

    Args:
        bstring: Base 64 encoded string to encode

    Returns:
        Decoded string
    """
    return base64.urlsafe_b64decode(bstring.encode("utf-8")).decode("utf-8")


def basicauth_encode(username: str, password: str) -> str:
    """Returns an HTTP basic authentication string given a username and
    password.

    Inspired by: https://github.com/rdegges/python-basicauth/blob/master/basicauth.py#L16

    Args:
        username: Username
        password: Password

    Returns:
        Basic authentication string
    """
    if ":" in username:
        raise ValueError

    username_password = f"{quote(username)}:{quote(password)}"
    return "Basic " + str_to_base64(username_password)


def basicauth_decode(encoded_string: str) -> tuple[str, str]:
    """Decode a HTTP basic authentication string. Returns a tuple of the form
    (username, password), and raises ValueError if decoding fails.

    Inspired by: https://github.com/rdegges/python-basicauth/blob/master/basicauth.py#L27

    Args:
        encoded_string: String to decode

    Returns:
        Tuple of form (username, password)
    """
    split_encoded_string = encoded_string.strip().split(" ")

    if len(split_encoded_string) == 1:
        info_index = 0
    elif (
        len(split_encoded_string) == 2
        and split_encoded_string[0].strip().lower() == "basic"
    ):
        info_index = 1
    else:
        raise ValueError(
            f"Authorization string {encoded_string} should have format "
            f'"xxxxxxxxxxxx" or "Basic xxxxxxxxxxxx"'
        )

    username, password = base64_to_str(split_encoded_string[info_index]).split(":", 1)
    return unquote(username), unquote(password)
