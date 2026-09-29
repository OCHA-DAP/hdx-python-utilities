import difflib
import re
from collections.abc import Callable, Sequence

from pyphonetics import RefinedSoundex
from rapidfuzz import fuzz as rapidfuzz_fuzz

from hdx.utilities.text import normalise

TEMPLATE_VARIABLES = re.compile("{{.*?}}")
NON_WORD_CHARACTERS = re.compile(r"[\W_]+")
LIST_SEPARATORS = re.compile(r"\s*(?:[,;/:&\n]|\s(?:and|et)\s)\s*", re.IGNORECASE)
HYPHEN = re.compile(r"\s*-\s*")


class Phonetics(RefinedSoundex):
    def match(
        self,
        possible_names: Sequence,
        name: str,
        alternative_name: str | None = None,
        transform_possible_names: Sequence[Callable] = [],
        threshold: int = 2,
    ) -> int | None:
        """
        Match name to one of the given possible names. Returns None if no match
        or the index of the matching name

        Args:
            possible_names: Possible names
            name: Name to match
            alternative_name: Alternative name to match. Defaults to None.
            transform_possible_names: Functions to transform possible names.
            threshold: Match threshold. Defaults to 2.

        Returns:
            Index of matching name from possible names or None
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


class RapidFuzzMatcher:
    """
    Default matcher for names, using rapidfuzz edit-distance scoring instead
    of phonetic (Soundex-family) encoding as Phonetics does. Phonetic algorithms
    encode English pronunciation rules, so they are a poor fit for matching
    multilingual or transliterated names (eg. "Sana'a" vs "Sanaa") that are
    spelling variants rather than being phonetically similar in English
    terms. Edit distance on normalised strings tends to place such variants
    closer together.

    Args:
        scorer: Function taking two strings and returning a similarity score
            from 0-100. Defaults to default_scorer. Use place_name_scorer for
            place names. Ties are broken by rapidfuzz.fuzz.ratio over the
            whole strings.

    Caveat: "<name> city" scores ~100 against "<name>", as for any name whose
    words are a subset of the other's. So withholding a text replacement that
    strips " city" does not stop "Kenge city" matching "Kenge".
    """

    def __init__(self, scorer: Callable[[str, str], float] | None = None) -> None:
        self.scorer = scorer or self.default_scorer

    @staticmethod
    def default_scorer(name: str, possible_name: str) -> float:
        """
        Score two strings with token_set_ratio, or with ratio on the strings
        with spaces and punctuation removed if that is at least 90 and higher.

        Args:
            name: Name to match
            possible_name: Possible name

        Returns:
            Similarity score from 0-100
        """
        score = rapidfuzz_fuzz.token_set_ratio(name, possible_name)
        joined_score = rapidfuzz_fuzz.ratio(
            NON_WORD_CHARACTERS.sub("", name),
            NON_WORD_CHARACTERS.sub("", possible_name),
        )
        if joined_score >= 90:
            return max(score, joined_score)
        return score

    @staticmethod
    def place_name_scorer(name: str, possible_name: str) -> float:
        """
        Score two strings with default_scorer, but score 0 if they share a
        word, each has other words of 3+ characters, and one of the words on
        the side with fewer has ratio < 60 to all those on the other side (eg.
        "central kalimantan" vs "kalimantan utara", but not "central west" vs
        "centre west"). Suits place names, where the differing word usually
        distinguishes places, but not names like sectors, where extra words
        are often descriptive (eg. "food security and livelihood").

        Args:
            name: Name to match
            possible_name: Possible name

        Returns:
            Similarity score from 0-100
        """
        words = set(name.split())
        possible_words = set(possible_name.split())

        def long_words(words: set[str]) -> set[str]:
            return {word for word in words if len(word) > 2}

        extra_words = long_words(words - possible_words)
        possible_extra_words = long_words(possible_words - words)
        if words & possible_words and extra_words and possible_extra_words:
            fewer, more = sorted((extra_words, possible_extra_words), key=len)
            for word in fewer:
                if max(rapidfuzz_fuzz.ratio(word, other) for other in more) < 60:
                    return 0.0
        return RapidFuzzMatcher.default_scorer(name, possible_name)

    def match(
        self,
        possible_names: Sequence,
        name: str,
        alternative_name: str | None = None,
        transform_possible_names: Sequence[Callable] = [],
        threshold: float = 65.0,
    ) -> int | None:
        """
        Match name to one of the given possible names. Returns None if no
        match or the index of the matching name.

        Args:
            possible_names: Possible names
            name: Name to match
            alternative_name: Alternative name to match. Defaults to None.
            transform_possible_names: Functions to transform possible names.
            threshold: Minimum similarity score, 0-100. Defaults to 65.0.

        Returns:
            Index of matching name from possible names or None
        """
        maxscore = None
        matching_index = None
        names = [name.lower()]
        if alternative_name:
            names.append(alternative_name.lower())
        all_transforms = (lambda x: x, *transform_possible_names)
        for i, possible_name in enumerate(possible_names):
            for transform_possible_name in all_transforms:
                transformed_possible_name = transform_possible_name(possible_name)
                if not transformed_possible_name:
                    continue
                transformed_possible_name = transformed_possible_name.lower()
                for query in names:
                    score = (
                        self.scorer(query, transformed_possible_name),
                        rapidfuzz_fuzz.ratio(query, transformed_possible_name),
                    )
                    if maxscore is None or score > maxscore:
                        maxscore = score
                        matching_index = i
        if maxscore is None or maxscore[0] < threshold:
            return None
        return matching_index


def split_name(name: str, separators: re.Pattern) -> list[str]:
    """
    Split name on separators, dropping parts that are empty once normalised.

    Args:
        name: Name to split
        separators: Compiled regular expression matching separators

    Returns:
        List of parts
    """
    parts = [part.strip() for part in separators.split(name)]
    return [part for part in parts if normalise(part)]


def resolve_name_parts(
    name: str, name_to_code: dict[str, str], ignore: str | None = None
) -> tuple[str | None, bool]:
    """
    Resolve a name made of parts split by separators (",", ";", "/", ":", "&",
    newline, "and", "et") or, if there are none, by a hyphen. Parts are looked
    up in name_to_code. A name with two parts gives a code if:
    - one part's normalised form equals ignore and the other part has a code
      (eg. "Falcón, Acosta" with the parent admin name "falcon")
    - one part's code followed by "-" starts the other's (eg. "Protection -
      GBV" gives PRO-GBV)
    - both parts have the same code.
    It is a list of names (eg. "Wash & Protection") if it has more than two
    parts, or two parts with different codes (eg. "Guba-Khachmaz").

    Args:
        name: Name to resolve
        name_to_code: Mapping from names (raw or normalised) to codes
        ignore: Normalised name of a part that qualifies the other part.
            Defaults to None.

    Returns:
        Tuple of code (or None) and whether name is a list of names
    """
    parts = split_name(name, LIST_SEPARATORS)
    if len(parts) > 2:
        return None, True
    if len(parts) < 2:
        parts = split_name(name, HYPHEN)
        if len(parts) != 2:
            return None, False
    normalised_parts = [normalise(part) for part in parts]
    if ignore in normalised_parts:
        index = 1 - normalised_parts.index(ignore)
        parts = [parts[index]]
        normalised_parts = [normalised_parts[index]]
    codes = []
    for part, normalised_part in zip(parts, normalised_parts):
        code = name_to_code.get(part, name_to_code.get(normalised_part))
        if not code:
            return None, False
        codes.append(code)
    code = codes[0]
    if len(codes) == 1:
        return code, False
    other_code = codes[1]
    if code == other_code or other_code.startswith(f"{code}-"):
        return other_code, False
    if code.startswith(f"{other_code}-"):
        return code, False
    return None, True


def get_code_from_name(
    name: str,
    code_lookup: dict[str, str],
    unmatched: list[str],
    fuzzy_match: bool = True,
    match_threshold: int = 5,
    matcher: Phonetics | RapidFuzzMatcher | None = None,
) -> str | None:
    """
    Given a name (org type, sector, etc), return the corresponding code. A
    name made of parts is resolved by resolve_name_parts, and is not fuzzy
    matched if it is a list of names.

    Args:
        name: Name to match
        code_lookup: Dictionary of official names and codes
        unmatched: List of unmatched names
        fuzzy_match: Allow fuzzy matching or not
        match_threshold: Match threshold
        matcher: Fuzzy matcher to use. Defaults to None (RapidFuzzMatcher).

    Returns:
        Matching code
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
    code, is_list = resolve_name_parts(name, code_lookup)
    if code:
        code_lookup[name] = code
        return code
    if not fuzzy_match or is_list:
        unmatched.append(name)
        return None
    names = [x for x in code_lookup.keys() if len(x) > match_threshold]
    if matcher is None:
        matcher = RapidFuzzMatcher()
    name_index = matcher.match(
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


def multiple_replace(string: str, replacements: dict[str, str]) -> str:
    """Simultaneously replace multiple strings in a string.

    Args:
        string: Input string
        replacements: Replacements dictionary

    Returns:
        String with replacements
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
) -> tuple[str | None, str | None]:
    """Try to match {{XXX}} in input string.

    Args:
        string: String in which to look for template

    Returns:
        (Matched string with brackets, matched string without brackets)
    """
    match = TEMPLATE_VARIABLES.search(string)
    if match:
        template_string = match.group()
        return template_string, template_string[2:-2]
    return None, None


def earliest_index(string_to_search: str, strings_to_try: Sequence[str]) -> int | None:
    """Search a string for each of a list of strings and return the earliest
    index.

    Args:
        string_to_search: String to search
        strings_to_try: Strings to try

    Returns:
        Earliest index of the strings to try in string to search or None
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
) -> list[str]:
    """Returns a list of matching blocks of text in a and b.

    Args:
        a: First string to match
        b: Second string to match
        match_min_size: Minimum block size to match on. Defaults to 30.
        ignore: Any characters to ignore in matching. Defaults to ''.
        end_characters: End characters to look for. Defaults to ''.

    Returns:
        List of matching blocks of text
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
    string_list: list[str],
    match_min_size: int = 30,
    ignore: str = "",
    end_characters: str = ".!\r\n",
) -> str:
    """Returns a string containing matching blocks of text in a list of strings
    followed by non-matching.

    Args:
        string_list: List of strings to match
        match_min_size: Minimum block size to match on. Defaults to 30.
        ignore: Any characters to ignore in matching. Defaults to ''.
        end_characters: End characters to look for. Defaults to '.\r\n'.

    Returns:
        String containing matching blocks of text followed by non-matching
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
    string_list: list[str],
    separator: str = "",
    match_min_size: int = 30,
    ignore: str = "",
    end_characters: str = ".!\r\n",
) -> str:
    """Returns a string containing matching blocks of text in a list of strings
    followed by non-matching.

    Args:
        string_list: List of strings to match
        separator: Separator to add between blocks of text. Defaults to ''.
        match_min_size: Minimum block size to match on. Defaults to 30.
        ignore: Any characters to ignore in matching. Defaults to ''.
        end_characters: End characters to look for. Defaults to '.\r\n'.

    Returns:
        String containing matching blocks of text followed by non-matching
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
