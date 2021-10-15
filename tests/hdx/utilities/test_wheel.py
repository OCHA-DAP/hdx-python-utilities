"""Version Tests"""
from os.path import join

import pytest

from hdx.utilities.wheel import get_version_from_whl


class TestWheel:
    @pytest.fixture(scope="class")
    def version_folder(self, fixturesfolder):
        return join(fixturesfolder, "wheel")

    def test_get_version_from_whl(self, version_folder):
        assert get_version_from_whl(version_folder) == "3.0.2"
