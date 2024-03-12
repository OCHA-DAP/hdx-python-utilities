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

    @pytest.fixture(scope="class")
    def multidatestatefile(self):
        return "analysis_dates.txt"

    @pytest.fixture(scope="class")
    def date1(self):
        return datetime(2020, 9, 23, 0, 0, tzinfo=timezone.utc)

    @pytest.fixture(scope="class")
    def date2(self):
        return datetime(2022, 5, 12, 10, 15, tzinfo=timezone.utc)

    def test_state(self, statefolder, statefile, date1, date2):
        with temp_dir(folder="test_state") as tmpdir:
            statepath = join(tmpdir, statefile)
            copyfile(join(statefolder, statefile), statepath)
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

    def test_multi_date_state(
        self, statefolder, multidatestatefile, date1, date2
    ):
        with temp_dir(folder="test_multidatestate") as tmpdir:
            statepath = join(tmpdir, multidatestatefile)
            copyfile(join(statefolder, multidatestatefile), statepath)
            with State(
                statepath,
                State.dates_str_to_country_date_dict,
                State.country_date_dict_to_dates_str,
            ) as state:
                state_dict = state.get()
                assert state_dict == {"DEFAULT": date1}
            with State(
                statepath,
                State.dates_str_to_country_date_dict,
                State.country_date_dict_to_dates_str,
            ) as state:
                state_dict = state.get()
                assert state_dict == {"DEFAULT": date1}
                state_dict["AFG"] = date2
                state.set(state_dict)
            with State(
                statepath,
                State.dates_str_to_country_date_dict,
                State.country_date_dict_to_dates_str,
            ) as state:
                state_dict = state.get()
                assert state_dict == {
                    "DEFAULT": date1,
                    "AFG": date2.replace(hour=0, minute=0),
                }
