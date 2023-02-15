"""State Utility Tests"""
from datetime import datetime, timezone
from os.path import join
from shutil import copyfile

import pytest

from hdx.utilities.dateparse import iso_string_from_datetime, parse_date
from hdx.utilities.path import temp_dir
from hdx.utilities.state import State


class TestState:
    @pytest.fixture(scope="class")
    def statefolder(self, fixturesfolder):
        return join(fixturesfolder, "state")

    @pytest.fixture(scope="class")
    def statefile(self):
        return "last_build_date.txt"

    def test_state(self, statefolder, statefile):
        with temp_dir(folder="test_state") as tmpdir:
            statepath = join(tmpdir, statefile)
            copyfile(join(statefolder, statefile), statepath)
            date1 = datetime(2020, 9, 23, 0, 0, tzinfo=timezone.utc)
            date2 = datetime(2022, 5, 12, 10, 15, tzinfo=timezone.utc)
            with State(
                statepath, parse_date, iso_string_from_datetime
            ) as state:
                assert state.get() == date1
            with State(
                statepath, parse_date, iso_string_from_datetime
            ) as state:
                assert state.get() == date1
                state.set(date2)
            with State(
                statepath, parse_date, iso_string_from_datetime
            ) as state:
                assert state.get() == date2.replace(hour=0, minute=0)
