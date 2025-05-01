"""Text processing utilities."""

import logging
import re
import string
import unicodedata
from string import punctuation
from typing import Any, List, Optional, Set

logger = logging.getLogger(__name__)


PUNCTUATION_MINUS_BRACKETS = r"""!"#$%&'*+,-./:;<=>?@\^_`|~"""

KEEP_CHARS_SAME = set(string.ascii_lowercase).union(set(string.digits))
CHANGE_TO_LOWERCASE = set(string.ascii_uppercase)
MAP_TO_SPACE = set(string.punctuation).union(set(string.whitespace))
MAP_TO_SPACE.remove("'")


def normalise(text: str) -> str:
    """
    Mormalise text for example to support name matching. Accented characters
    are replaced with non-accented if possible. Any punctuation and whitespace
    is replaced with a space except for ' which is replaced with blank.
    Multiple spaces are replaced with a single space. Uppercase is replaced
    with lowercase. Spaces at start and end are removed. All non-ASCII
    characters are removed.

    Args:
        text (str): Text to normalise

    Returns:
        str: Normalised text
    """
    chars = []
    space = False
    for chr in unicodedata.normalize("NFD", text):
        if chr in KEEP_CHARS_SAME:
            chars.append(chr)
            space = False
        elif chr in CHANGE_TO_LOWERCASE:
            chars.append(chr.lower())
            space = False
        elif chr in MAP_TO_SPACE:
            if space:
                continue
            chars.append(" ")
            space = True
    return "".join(chars).strip()


def remove_end_characters(string: str, characters_to_remove: str = punctuation) -> str:
    """Remove any characters at end of string that are in characters_to_remove.

    Args:
        string (str): Input string
        characters_to_remove (str): Characters to remove. Defaults to punctuation.

    Returns:
        str: String with any characters at end of string that are in characters_to_remove removed
    """
    while string[-1] in characters_to_remove:
        string = string[:-1]
    return string


def remove_from_end(
    string: str,
    things_to_remove: List[str],
    logging_text: Optional[str] = None,
    whole_words: bool = True,
) -> str:
    """Remove list of items from end of string, stripping any whitespace.

    Args:
        string (str): Input string
        things_to_remove (List[str]): Things to remove from the end of string
        logging_text (Optional[str]): Text to log. Defaults to None.
        whole_words (bool): Remove parts of or whole words. Defaults to True (whole words only).

    Returns:
        str: String with text removed
    """
    for thing in things_to_remove:
        thing_len = len(thing)
        string_len = len(string)
        if string_len <= thing_len + 1:
            continue
        position = -thing_len
        if string[position:] != thing:
            continue
        if whole_words and string[position - 1].isalpha():
            continue
        newstring = string[:position].strip()
        if logging_text:
            logger.info(logging_text % (string, newstring))
        string = newstring
    return string


def remove_string(
    string: str, toremove: str, end_characters_to_remove: str = punctuation
) -> str:
    """
    Remove string from another string and delete any preceding end characters - by default punctuation (eg. comma)
    and any whitespace following the punctuation

    Args:
        string (str): String to process
        toremove (str): String to remove
        end_characters_to_remove (str): Characters to remove. Defaults to punctuation.

    Returns:
        str: String with other string removed

    """
    index = string.find(toremove)
    newstring = string[:index].strip()
    newstring = remove_end_characters(
        newstring, characters_to_remove=end_characters_to_remove
    )
    return f"{newstring}{string[index + len(toremove) :]}"


def get_words_in_sentence(sentence: str) -> List[str]:
    """Returns list of words in a sentence.

    Args:
        sentence (str): Sentence

    Returns:
        List[str]: List of words in sentence
    """
    return re.sub("[" + punctuation.replace("'", "") + "]", " ", sentence).split()


def number_format(val: Any, format: str = "%.4f", trailing_zeros: bool = True) -> str:
    """Format float-castable input as string.

    Args:
        val (float): Number to format
        format (str): Format to use. Defaults to %.4f.
        trailing_zeros (bool): Leave trailing zeros. Defaults to True.

    Returns:
        str: Formatted number as string
    """
    if val == "" or val is None:
        return ""
    val = format % float(val)
    if trailing_zeros:
        return val
    return val.rstrip("0").rstrip(".")


def get_fraction_str(
    numerator: Any,
    denominator: Optional[Any] = None,
    format: str = "%.4f",
    trailing_zeros: bool = True,
) -> str:
    """Given float-castable numerator and optional float-castable denominator,
    format as string, returning '' for invalid numerator or 0 denominator.

    Args:
        numerator (float): Numerator
        denominator (Optional[float]): Denominator. Defaults to None.
        format (str): Format to use. Defaults to %.4f.
        trailing_zeros (bool): Leave trailing zeros. Defaults to True.

    Returns:
        str: Formatted number as string
    """
    try:
        numerator = float(numerator)
        if denominator:
            numerator /= float(denominator)
        else:
            if denominator is not None:
                return ""
        return number_format(numerator, format, trailing_zeros)
    except ValueError:
        pass
    return ""


def only_allowed_in_str(test_str: str, allowed_chars: Set) -> bool:
    """Returns True if test string contains only allowed characters, False if
    not.

    Args:
        test_str (str): Test string
        allowed_chars (Set): Set of allowed characters

    Returns:
        bool: True if test string contains only allowed characters, False if not
    """
    return set(test_str) <= allowed_chars


allowed_numeric = set(string.digits + "." + "," + "%" + "-")


def get_numeric_if_possible(value: Any) -> Any:
    """Return val if it is not a string, otherwise see if it can be cast to
    float or int, taking into account commas and periods.

    Args:
        value (Any): Value

    Returns:
        Any: Value
    """

    def get_int_value(val, denominator):
        val = int(val)
        if denominator != 1:
            return float(val) / denominator
        else:
            return val

    if isinstance(value, str):
        val = value.strip()
        if val != "" and only_allowed_in_str(val, allowed_numeric):
            try:
                minusindex = val.index("-")
                if minusindex != 0:
                    return val
            except ValueError:
                pass
            try:
                commaindex = val.index(",")
            except ValueError:
                commaindex = None
            try:
                dotindex = val.index(".")
            except ValueError:
                dotindex = None
            if val[-1] == "%":
                denominator = 100
                val = val[:-1]
            else:
                denominator = 1
            if commaindex is None:
                if dotindex is None:
                    return get_int_value(val, denominator)
                else:
                    if val.count(".") == 1:
                        return float(val) / denominator
                    else:
                        return get_int_value(val.replace(".", ""), denominator)
            else:
                if dotindex is None:
                    return get_int_value(val.replace(",", ""), denominator)
                else:
                    if dotindex > commaindex:
                        val = val.replace(",", "")
                    else:
                        val = val.replace(".", "")
                        val = val.replace(",", ".")
                    return float(val) / denominator
    return value
