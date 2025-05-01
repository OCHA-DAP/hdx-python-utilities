import difflib
import re
from typing import Callable, Dict, List, Optional, Tuple

from pyphonetics import RefinedSoundex

from .text import normalise
from .typehint import ListTuple

TEMPLATE_VARIABLES = re.compile("{{.*?}}")


class Phonetics(RefinedSoundex):
    def match(
        self,
        possible_names: ListTuple,
        name: str,
        alternative_name: Optional[str] = None,
        transform_possible_names: ListTuple[Callable] = [],
        threshold: int = 2,
    ) -> Optional[int]:
        """
        Match name to one of the given possible names. Returns None if no match
        or the index of the matching name

        Args:
            possible_names (ListTuple): Possible names
            name (str): Name to match
            alternative_name (str): Alternative name to match. Defaults to None.
            transform_possible_names (ListTuple[Callable]): Functions to transform possible names.
            threshold: Match threshold. Defaults to 2.

        Returns:
            Optional[int]: Index of matching name from possible names or None
        """
        mindistance = None
        matching_index = None

        transform_possible_names.insert(0, lambda x: x)

        def check_name(name, possible_name):
            nonlocal mindistance, matching_index  # noqa: E999

            distance = self.distance(name, possible_name)
            if mindistance is None or distance < mindistance:
                mindistance = distance
                matching_index = i

        for i, possible_name in enumerate(possible_names):
            for transform_possible_name in transform_possible_names:
                transformed_possible_name = transform_possible_name(possible_name)
                if not transformed_possible_name:
                    continue
                check_name(name, transformed_possible_name)
                if alternative_name:
                    check_name(alternative_name, transformed_possible_name)
        if mindistance is None or mindistance > threshold:
            return None
        return matching_index


def get_code_from_name(
    name: str,
    code_lookup: Dict[str, str],
    unmatched: List[str],
    fuzzy_match: bool = True,
    match_threshold: int = 5,
) -> Optional[str]:
    """
    Given a name (org type, sector, etc), return the corresponding code.

    Args:
        name (str): Name to match
        code_lookup (dict): Dictionary of official names and codes
        unmatched (List[str]): List of unmatched names
        fuzzy_match (bool): Allow fuzzy matching or not
        match_threshold (int): Match threshold

    Returns:
        Optional[str]: Matching code
    """
    code = code_lookup.get(name)
    if code:
        return code
    if name in unmatched:
        return None
    name_clean = normalise(name)
    code = code_lookup.get(name_clean)
    if code:
        code_lookup[name] = code
        return code
    if len(name) <= match_threshold:
        unmatched.append(name)
        return None
    if not fuzzy_match:
        unmatched.append(name)
        return None
    names = [x for x in code_lookup.keys() if len(x) > match_threshold]
    name_index = Phonetics().match(
        possible_names=names,
        name=name,
        alternative_name=name_clean,
    )
    if name_index is None:
        unmatched.append(name)
        return None
    code = code_lookup.get(names[name_index])
    if code:
        code_lookup[name] = code
        code_lookup[name_clean] = code
    return code


def multiple_replace(string: str, replacements: Dict[str, str]) -> str:
    """Simultaneously replace multiple strings in a string.

    Args:
        string (str): Input string
        replacements (Dict[str,str]): Replacements dictionary

    Returns:
        str: String with replacements
    """
    if not replacements:
        return string
    pattern = re.compile(
        "|".join([re.escape(k) for k in sorted(replacements, key=len, reverse=True)]),
        flags=re.DOTALL,
    )
    return pattern.sub(lambda x: replacements[x.group(0)], string)


def match_template_variables(
    string: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Try to match {{XXX}} in input string.

    Args:
        string (str): String in which to look for template

    Returns:
        Tuple[Optional[str], Optional[str]]: (Matched string with brackets, matched string without brackets)
    """
    match = TEMPLATE_VARIABLES.search(string)
    if match:
        template_string = match.group()
        return template_string, template_string[2:-2]
    return None, None


def earliest_index(
    string_to_search: str, strings_to_try: ListTuple[str]
) -> Optional[int]:
    """Search a string for each of a list of strings and return the earliest
    index.

    Args:
        string_to_search (str): String to search
        strings_to_try (ListTuple[str]): Strings to try

    Returns:
        Optional[int]: Earliest index of the strings to try in string to search or None
    """
    after_string = len(string_to_search) + 1
    indices = []
    for string_to_try in strings_to_try:
        try:
            index = string_to_search.index(string_to_try)
            indices.append(index)
        except ValueError:
            indices.append(after_string)
    earliest_index = sorted(indices)[0]
    if earliest_index == after_string:
        return None
    else:
        return earliest_index


def get_matching_text_in_strs(
    a: str,
    b: str,
    match_min_size: int = 30,
    ignore: str = "",
    end_characters: str = "",
) -> List[str]:
    """Returns a list of matching blocks of text in a and b.

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
    matching_text = []

    for match in compare.get_matching_blocks():
        start = match.a
        text = a[start : start + match.size]
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


def get_matching_text(
    string_list: List[str],
    match_min_size: int = 30,
    ignore: str = "",
    end_characters: str = ".!\r\n",
) -> str:
    """Returns a string containing matching blocks of text in a list of strings
    followed by non-matching.

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
        result = get_matching_text_in_strs(
            a,
            b,
            match_min_size=match_min_size,
            ignore=ignore,
            end_characters=end_characters,
        )
        a = "".join(result)
    return a


def get_matching_then_nonmatching_text(
    string_list: List[str],
    separator: str = "",
    match_min_size: int = 30,
    ignore: str = "",
    end_characters: str = ".!\r\n",
) -> str:
    """Returns a string containing matching blocks of text in a list of strings
    followed by non-matching.

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
        if (
            separator
            and len(text_list) > 0
            and text_list[-1][-len(separator) :] != separator
        ):
            text_list.append(separator)

    a = string_list[0]
    for i in range(1, len(string_list)):
        b = string_list[i]
        combined_len = len(a) + len(b)
        result = get_matching_text_in_strs(
            a,
            b,
            match_min_size=match_min_size,
            ignore=ignore,
            end_characters=end_characters,
        )
        new_a = a
        new_b = b
        for text in result:
            new_a = new_a.replace(text, "")
            new_b = new_b.replace(text, "")
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
        output = []
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
        a = "".join(output)
    return a
