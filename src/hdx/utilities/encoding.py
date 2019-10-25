# -*- coding: utf-8 -*-
"""Encoding utilities"""

import base64


def str_to_base64(string):
    # type: (str) -> str
    """
    Base 64 encode string

    Args:
        string (str): String to encode

    Returns:
        str: Base 64 encoded string

    """
    return base64.urlsafe_b64encode(string.encode('utf-8')).decode('utf-8')


def base64_to_str(bstring):
    # type: (str) -> str
    """
    Base 64 decode string

    Args:
        bstring (str): Base 64 encoded string to encode

    Returns:
        str: Decoded string

    """
    return base64.urlsafe_b64decode(bstring.encode('utf-8')).decode('utf-8')
