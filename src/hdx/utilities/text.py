# -*- coding: utf-8 -*-
"""Text processing utilities"""
import difflib
import logging
import re
import string
from string import punctuation
from typing import List, Dict, Optional, Set, Any

logger = logging.getLogger(__name__)

PUNCTUATION_MINUS_BRACKETS = r"""!"#$%&'*+,-./:;<=>?@\^_`|~"""


def remove_end_characters(string, characters_to_remove=punctuation):
    # type: (str, str) -> str
    """Remove any characters at end of string that are in characters_to_remove

    Args:
        string (str): Input string
        characters_to_remove (str): Characters to remove. Defaults to punctuation.

    Returns:
        str: String with any characters at end of string that are in characters_to_remove removed

    """
    while string[-1] in characters_to_remove:
        string = string[:-1]
    return string


def remove_from_end(string, things_to_remove, logging_text=None, whole_words=True):
    # type: (str, List[str], Optional[str], bool) -> str
    """Remove list of items from end of string, stripping any whitespace

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


def remove_string(string, toremove, end_characters_to_remove=punctuation):
    # type: (str, str, str) -> str
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
    newstring = remove_end_characters(newstring, characters_to_remove=end_characters_to_remove)
    return '%s%s' % (newstring, string[index + len(toremove):])


def multiple_replace(string, replacements):
    # type: (str, Dict[str,str]) -> str
    """Simultaneously replace multiple strings in a string

    Args:
        string (str): Input string
        replacements (Dict[str,str]): Replacements dictionary

    Returns:
        str: String with replacements

    """
    if not replacements:
        return string
    pattern = re.compile("|".join([re.escape(k) for k in sorted(replacements, key=len, reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: replacements[x.group(0)], string)


def get_words_in_sentence(sentence):
    # type: (str) -> List[str]
    """Returns list of words in a sentence

    Args:
        sentence (str): Sentence

    Returns:
        List[str]: List of words in sentence

    """
    return re.sub('[' + punctuation.replace("'", "") + ']', ' ', sentence).split()


def get_matching_text_in_strs(a, b, match_min_size=30, ignore='', end_characters=''):
    # type: (str, str, int, str, str) -> List[str]
    """Returns a list of matching blocks of text in a and b

    Args:
        a (str): First string to match
        b (str): Second string to match
        match_min_size (int): Minimum block size to match on. Defaults to 30.
        ignore (str): Any characters to ignore in matching. Defaults to ''.
        end_characters (str): End characters to look for. Defaults to ''.

    Returns:
        List[str]: List of matching blocks of text

    """
    compare = difflib.SequenceMatcher(lambda x: x in ignore)
    compare.set_seqs(a=a, b=b)
    matching_text = list()

    for match in compare.get_matching_blocks():
        start = match.a
        text = a[start: start+match.size]
        if end_characters:
            prev_text = text
            while len(text) != 0 and text[0] in end_characters:
                text = text[1:]
            while len(text) != 0 and text[-1] not in end_characters:
                text = text[:-1]
            if len(text) == 0:
                text = prev_text
        if len(text) >= match_min_size:
            matching_text.append(text)
    return matching_text


def get_matching_text(string_list, match_min_size=30, ignore='', end_characters='.!\r\n'):
    # type: (List[str], int, str, str) -> str
    """Returns a string containing matching blocks of text in a list of strings followed by non-matching.

    Args:
        string_list (List[str]): List of strings to match
        match_min_size (int): Minimum block size to match on. Defaults to 30.
        ignore (str): Any characters to ignore in matching. Defaults to ''.
        end_characters (str): End characters to look for. Defaults to '.\r\n'.

    Returns:
        str: String containing matching blocks of text followed by non-matching

    """
    a = string_list[0]
    for i in range(1, len(string_list)):
        b = string_list[i]
        result = get_matching_text_in_strs(a, b, match_min_size=match_min_size, ignore=ignore,
                                           end_characters=end_characters)
        a = ''.join(result)
    return a


def get_matching_then_nonmatching_text(string_list, separator='', match_min_size=30, ignore='',
                                       end_characters='.!\r\n'):
    # type: (List[str], str, int, str, str) -> str
    """Returns a string containing matching blocks of text in a list of strings followed by non-matching.

    Args:
        string_list (List[str]): List of strings to match
        separator (str): Separator to add between blocks of text. Defaults to ''.
        match_min_size (int): Minimum block size to match on. Defaults to 30.
        ignore (str): Any characters to ignore in matching. Defaults to ''.
        end_characters (str): End characters to look for. Defaults to '.\r\n'.

    Returns:
        str: String containing matching blocks of text followed by non-matching

    """
    def add_separator_if_needed(text_list):
        if separator and len(text_list) > 0 and text_list[-1][-len(separator):] != separator:
            text_list.append(separator)

    a = string_list[0]
    for i in range(1, len(string_list)):
        b = string_list[i]
        combined_len = len(a) + len(b)
        result = get_matching_text_in_strs(a, b, match_min_size=match_min_size, ignore=ignore,
                                           end_characters=end_characters)
        new_a = a
        new_b = b
        for text in result:
            new_a = new_a.replace(text, '')
            new_b = new_b.replace(text, '')
        if new_a and new_a in a:
            pos_a = a.index(new_a)
        else:
            pos_a = combined_len
        if new_b and new_b in b:
            pos_b = b.index(new_b)
        else:
            pos_b = combined_len
        if pos_b > pos_a:
            text_1 = new_b
            pos_1 = pos_b
            text_2 = new_a
            pos_2 = pos_a
        else:
            text_1 = new_a
            pos_1 = pos_a
            text_2 = new_b
            pos_2 = pos_b
        output = list()
        pos = 0
        for text in result:
            output.append(text)
            pos += len(text)
            if text_1 and pos >= pos_1:
                add_separator_if_needed(output)
                output.append(text_1)
                pos += len(text_1)
                text_1 = None
            if text_2 and pos >= pos_2:
                add_separator_if_needed(output)
                output.append(text_2)
                pos += len(text_2)
                text_2 = None
        if text_1 and pos_1 == combined_len:
            add_separator_if_needed(output)
            output.append(text_1)
        if text_2 and pos_2 == combined_len:
            add_separator_if_needed(output)
            output.append(text_2)
        a = ''.join(output)
    return a


def number_format(val, format='%.4f', trailing_zeros=True):
    # type: (Any, str, bool) -> str
    """Format float-castable input as string

    Args:
        val (float): Number to format
        format (str): Format to use. Defaults to %.4f.
        trailing_zeros (bool): Leave trailing zeros. Defaults to True.

    Returns:
        str: Formatted number as string
    """
    if val == '' or val is None:
        return ''
    val = format % float(val)
    if trailing_zeros:
        return val
    return val.rstrip('0').rstrip('.')


def get_fraction_str(numerator, denominator=None, format='%.4f', trailing_zeros=True):
    # type: (Any, Optional[Any], str, bool) -> str
    """Given float-castable numerator and optional float-castable denominator, format as string, returning '' for
    invalid numerator or 0 denominator.

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
                return ''
        return number_format(numerator, format, trailing_zeros)
    except ValueError:
        pass
    return ''


def only_allowed_in_str(test_str, allowed_chars):
    # type: (str, Set) -> bool
    """Returns True if test string contains only allowed characters, False if not.

    Args:
        test_str (str): Test string
        allowed_chars (Set): Set of allowed characters

    Returns:
        bool: True if test string contains only allowed characters, False if not
    """
    return set(test_str) <= allowed_chars


allowed_numeric = set(string.digits + '.' + ',' + '%' + '-')


def get_numeric_if_possible(value):
    # type: (Any) -> Any
    """Return val if it is not a string, otherwise see if it can be cast to float or int,
    taking into account commas and periods.

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
        if val != '' and only_allowed_in_str(val, allowed_numeric):
            try:
                minusindex = val.index('-')
                if minusindex != 0:
                    return val
            except ValueError:
                pass
            try:
                commaindex = val.index(',')
            except ValueError:
                commaindex = None
            try:
                dotindex = val.index('.')
            except ValueError:
                dotindex = None
            if val[-1] == '%':
                denominator = 100
                val = val[:-1]
            else:
                denominator = 1
            if commaindex is None:
                if dotindex is None:
                    return get_int_value(val, denominator)
                else:
                    if val.count('.') == 1:
                        return float(val) / denominator
                    else:
                        return get_int_value(val.replace('.', ''), denominator)
            else:
                if dotindex is None:
                    return get_int_value(val.replace(',', ''), denominator)
                else:
                    if dotindex > commaindex:
                        val = val.replace(',', '')
                    else:
                        val = val.replace('.', '')
                        val = val.replace(',', '.')
                    return float(val) / denominator
    return value
