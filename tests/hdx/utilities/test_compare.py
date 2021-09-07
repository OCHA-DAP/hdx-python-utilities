"""Compare Utility Tests"""
from os.path import join

import pytest

from hdx.utilities.compare import assert_files_same, compare_files


class TestCompare:
    @pytest.fixture(scope="class")
    def testfile1(self, fixturesfolder):
        return join(fixturesfolder, "compare", "test_csv_processing.csv")

    @pytest.fixture(scope="class")
    def testfile2(self, fixturesfolder):
        return join(fixturesfolder, "compare", "test_csv_processing2.csv")

    def test_compare_files(self, testfile1, testfile2):
        result = compare_files(testfile1, testfile2)
        assert result == [
            "- coal   ,3      ,7.4    ,'needed'",
            "?         ^\n",
            "+ coal   ,1      ,7.4    ,'notneeded'",
            "?         ^                +++\n",
        ]
        assert_files_same(testfile1, testfile1)
