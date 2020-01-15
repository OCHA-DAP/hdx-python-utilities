# -*- coding: UTF-8 -*-
"""Date Parse Utility Tests"""
from datetime import datetime

import pytest

from hdx.utilities.dateparse import parse_date_range, parse_date


class TestDateParse:
    def test_parse_date_range(self):
        result = datetime(2013, 2, 20, 0, 0), datetime(2013, 2, 20, 0, 0)
        assert parse_date_range('20/02/2013') == result
        assert parse_date_range('20/02/2013 10:00:00') == result
        assert parse_date_range('20/02/2013', '%d/%m/%Y') == result
        assert parse_date_range('20/02/2013 10:00:00', '%d/%m/%Y %H:%M:%S') == result
        fuzzy = dict()
        assert parse_date_range('date is 20/02/2013 for this test', fuzzy=fuzzy) == result
        fuzzyresult = {'startdate': datetime(2013, 2, 20, 0, 0), 'enddate': datetime(2013, 2, 20, 0, 0),
                       'nondate': ('date is ', ' for this test'), 'date': ('20/02/2013',)}
        assert fuzzy == fuzzyresult
        fuzzy = dict()
        assert parse_date_range('date is 20/02/2013 for this test', date_format='%d/%m/%Y', fuzzy=fuzzy) == result
        assert fuzzy == fuzzyresult
        fuzzy = dict()
        assert parse_date_range('20/02/2013', date_format='%d/%m/%Y', fuzzy=fuzzy) == result
        fuzzyresult['nondate'] = None
        assert fuzzy == fuzzyresult
        result = datetime(2013, 2, 1, 0, 0), datetime(2013, 2, 28, 0, 0)
        assert parse_date_range('02/2013') == result
        assert parse_date_range('02/2013', '%m/%Y') == result
        fuzzy = dict()
        assert parse_date_range('date is 02/2013 for this test', fuzzy=fuzzy) == result
        assert fuzzy == {'startdate': datetime(2013, 2, 1, 0, 0), 'enddate': datetime(2013, 2, 28, 0, 0),
                         'nondate': ('date is ', ' for this test'), 'date': ('02/2013',)}
        result = datetime(2013, 1, 1, 0, 0), datetime(2013, 12, 31, 0, 0)
        assert parse_date_range('2013') == result
        assert parse_date_range('2013', '%Y') == result
        with pytest.raises(ValueError):
            fuzzy = dict()
            parse_date_range('Mon_State_Village_Tract_Boundaries', fuzzy=fuzzy)
        with pytest.raises(ValueError):
            parse_date_range('20/02')
        with pytest.raises(ValueError):
            parse_date_range('02/20')
        with pytest.raises(ValueError):
            parse_date_range('20/02', '%d/%m')

    def test_parse_date(self):
        assert parse_date('20/02/2013') == datetime(2013, 2, 20, 0, 0)
        assert parse_date('20/02/2013', '%d/%m/%Y') == datetime(2013, 2, 20, 0, 0)
        with pytest.raises(ValueError):
            parse_date('02/2013')
        with pytest.raises(ValueError):
            parse_date('02/2013', '%m/%Y')
