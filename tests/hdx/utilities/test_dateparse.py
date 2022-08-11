"""Date Parse Utility Tests"""
from datetime import datetime, timedelta, timezone

import pytest
from dateutil.parser import ParserError

from hdx.utilities.dateparse import (
    get_datetime_from_timestamp,
    get_timestamp_from_datetime,
    now_utc,
    parse_date,
    parse_date_range,
)


class TestDateParse:
    def test_now_utc(self):
        assert now_utc().replace(
            second=0, microsecond=0
        ) == datetime.utcnow().replace(
            second=0, microsecond=0, tzinfo=timezone.utc
        )

    def test_parse_date_range(self):
        result = datetime(2013, 2, 10, 0, 0, tzinfo=timezone.utc), datetime(
            2013, 2, 10, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date_range("10/02/2013") == result
        assert parse_date_range("2013/02/10") == result
        result = datetime(2013, 2, 20, 10, 0, tzinfo=timezone.utc), datetime(
            2013, 2, 20, 10, 0, tzinfo=timezone.utc
        )
        assert parse_date_range("20/02/2013 10:00:00") == result
        assert (
            parse_date_range("20/02/2013 10:00:00", "%d/%m/%Y %H:%M:%S")
            == result
        )
        result = datetime(2013, 2, 20, 0, 0, tzinfo=timezone.utc), datetime(
            2013, 2, 20, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date_range("20/02/2013") == result
        assert (
            parse_date_range("20/02/2013 10:00:00", zero_time=True) == result
        )
        result2 = datetime(2013, 2, 20, 0, 0, tzinfo=timezone.utc), datetime(
            2013, 2, 20, 23, 59, 59, tzinfo=timezone.utc
        )
        assert (
            parse_date_range(
                "20/02/2013 10:00:00",
                zero_time=True,
                max_endtime=True,
            )
            == result2
        )
        result2 = (
            datetime(2013, 2, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            datetime(2013, 2, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
        )
        assert (
            parse_date_range(
                "20/02/2013 10:00:00",
                include_microseconds=True,
                max_starttime=True,
                max_endtime=True,
            )
            == result2
        )
        assert parse_date_range("20/02/2013", "%d/%m/%Y") == result
        assert (
            parse_date_range(
                "20/02/2013 10:00:00", "%d/%m/%Y %H:%M:%S", zero_time=True
            )
            == result
        )
        fuzzy = dict()
        assert (
            parse_date_range("date is 20/02/2013 for this test", fuzzy=fuzzy)
            == result
        )
        fuzzyresult = {
            "startdate": datetime(2013, 2, 20, 0, 0, tzinfo=timezone.utc),
            "enddate": datetime(2013, 2, 20, 0, 0, tzinfo=timezone.utc),
            "nondate": ("date is ", " for this test"),
            "date": ("20/02/2013",),
        }
        assert fuzzy == fuzzyresult
        fuzzy = dict()
        assert (
            parse_date_range(
                "date is 20/02/2013 for this test",
                date_format="%d/%m/%Y",
                fuzzy=fuzzy,
            )
            == result
        )
        assert fuzzy == fuzzyresult
        fuzzy = dict()
        assert (
            parse_date_range("20/02/2013", date_format="%d/%m/%Y", fuzzy=fuzzy)
            == result
        )
        fuzzyresult["nondate"] = None
        assert fuzzy == fuzzyresult
        result = datetime(2013, 2, 1, 0, 0, tzinfo=timezone.utc), datetime(
            2013, 2, 28, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date_range("02/2013") == result
        assert parse_date_range("02/2013", "%m/%Y") == result
        fuzzy = dict()
        assert (
            parse_date_range("date is 02/2013 for this test", fuzzy=fuzzy)
            == result
        )
        assert fuzzy == {
            "startdate": datetime(2013, 2, 1, 0, 0, tzinfo=timezone.utc),
            "enddate": datetime(2013, 2, 28, 0, 0, tzinfo=timezone.utc),
            "nondate": ("date is ", " for this test"),
            "date": ("02/2013",),
        }
        result = datetime(2013, 1, 1, 0, 0, tzinfo=timezone.utc), datetime(
            2013, 12, 31, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date_range("2013") == result
        assert parse_date_range("2013", "%Y") == result
        fuzzy = dict()
        date = datetime(2001, 12, 10, 0, 0, tzinfo=timezone.utc)
        result = date, date
        assert (
            parse_date_range(
                "State_Village_Tract_Boundaries 10/12/01 lala", fuzzy=fuzzy
            )
            == result
        )
        assert fuzzy == {
            "startdate": date,
            "enddate": date,
            "nondate": ("State_Village_Tract_Boundaries ", " lala"),
            "date": ("10/12/01",),
        }
        with pytest.raises(ParserError):
            parse_date_range("lalala", "%d/%m/%Y")
        with pytest.raises(ParserError):
            parse_date_range("State_Village_Tract_Boundaries", fuzzy=dict())
        with pytest.raises(ParserError):
            fuzzy = dict()
            parse_date_range("Mon_State_Village_Tract_Boundaries", fuzzy=fuzzy)
        with pytest.raises(ParserError):
            parse_date_range("20/02")
        with pytest.raises(ParserError):
            parse_date_range("02/20")
        with pytest.raises(ParserError):
            parse_date_range("20/02", "%d/%m")

    def test_parse_date(self):
        assert parse_date("20/02/2013") == datetime(
            2013, 2, 20, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date("20/02/2013", "%d/%m/%Y") == datetime(
            2013, 2, 20, 0, 0, tzinfo=timezone.utc
        )
        assert parse_date("20/02/2013 01:30:20") == datetime(
            2013, 2, 20, 1, 30, 20, tzinfo=timezone.utc
        )
        assert parse_date("20/02/2013 01:30:20 IST") == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone.utc,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST", timezone_handling=1
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST",
            timezone_handling=2,
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone(timedelta(hours=5, minutes=30)),
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST",
            timezone_handling=3,
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone(timedelta(hours=5, minutes=30)),
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST", timezone_handling=4
        ) == datetime(
            2013,
            2,
            19,
            20,
            00,
            20,
            tzinfo=timezone.utc,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST", zero_time=True
        ) == datetime(
            2013,
            2,
            20,
            0,
            0,
            0,
            tzinfo=timezone.utc,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST", max_time=True
        ) == datetime(
            2013,
            2,
            20,
            23,
            59,
            59,
            tzinfo=timezone.utc,
        )
        assert parse_date(
            "20/02/2013 01:30:20 NUT",
            timezone_handling=2,
            default_timezones="-11 X NUT SST",
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone(timedelta(hours=-11)),
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST",
            timezone_handling=2,
            default_timezones="-11 X NUT SST",
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST",
            timezone_handling=3,
            default_timezones="-11 X NUT SST",
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone.utc,
        )
        assert parse_date(
            "20/02/2013 01:30:20 IST",
            timezone_handling=5,
            default_timezones="-11 X NUT SST",
        ) == datetime(
            2013,
            2,
            20,
            1,
            30,
            20,
            tzinfo=timezone.utc,
        )
        with pytest.raises(ParserError):
            parse_date("02/2013")
        with pytest.raises(ParserError):
            parse_date("02/2013", "%m/%Y")

    def test_get_datetime_from_timestamp(self):
        expected_timestamp = 1596180834.0
        expected_date = datetime(2020, 7, 31, 7, 33, 54, tzinfo=timezone.utc)
        timestamp = get_timestamp_from_datetime(expected_date)
        assert timestamp == expected_timestamp
        date = get_datetime_from_timestamp(
            expected_timestamp, timezone=timezone.utc
        )
        assert date == expected_date
        date = get_datetime_from_timestamp(
            expected_timestamp * 1000, timezone=timezone.utc
        )
        assert date == expected_date
