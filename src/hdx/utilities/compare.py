"""File compare utilities"""
import difflib
from os import linesep
from typing import List


def compare_files(path1: str, path2: str) -> List[str]:
    """Returns the delta between two files using -, ?, + format excluding
    lines that are the same

    Args:
        path1 (str): Path to first file
        path2 (str): Path to second file

    Returns:
        List[str]: Delta between the two files

    """
    diff = difflib.ndiff(
        open(path1).read().splitlines(), open(path2).read().splitlines()
    )
    return [x for x in diff if x[0] in ["-", "+", "?"]]


def assert_files_same(path1: str, path2: str) -> None:
    """Asserts that two files are the same and returns delta using
    -, ?, + format if not

    Args:
        path1 (str): Path to first file
        path2 (str): Path to second file

    Returns:
        None

    """
    difflines = compare_files(path1, path2)
    assert len(difflines) == 0, linesep.join([linesep] + difflines)
