# -*- coding: UTF-8 -*-
"""Date Parse Utility Tests"""
from datetime import datetime

import pytest

from hdx.utilities.dateparse import parse_date_or_range, parse_date


class TestDateParse:
    def test_parse_date_or_range(self):
        assert parse_date_or_range('20/02/2013') == {'enddate': None, 'date': datetime(2013, 2, 20, 0, 0),
                                                     'nondate': None}
        assert parse_date_or_range('20/02/2013 10:00:00') == {'enddate': None, 'date': datetime(2013, 2, 20, 0, 0),
                                                              'nondate': None}
        assert parse_date_or_range('20/02/2013', '%d/%m/%Y') == {'enddate': None, 'date': datetime(2013, 2, 20, 0, 0),
                                                                 'nondate': None}
        assert parse_date_or_range('20/02/2013 10:00:00', '%d/%m/%Y %H:%M:%S') == {'enddate': None,
                                                                                   'date': datetime(2013, 2, 20, 0, 0),
                                                                                   'nondate': None}
        assert parse_date_or_range('date is 20/02/2013 for this test', fuzzy=True) == {'enddate': None,
                                                                                       'date': datetime(2013, 2, 20, 0,
                                                                                                        0), 'nondate': (
            'date is ', ' for this test')}
        assert parse_date_or_range('date is 20/02/2013 for this test', date_format='%d/%m/%Y', fuzzy=True) == {
            'enddate': None, 'date': datetime(2013, 2, 20, 0, 0), 'nondate': ('date is ', ' for this test')}
        assert parse_date_or_range('02/2013') == {'enddate': datetime(2013, 2, 28, 0, 0),
                                                  'date': datetime(2013, 2, 1, 0, 0), 'nondate': None}
        assert parse_date_or_range('02/2013', '%m/%Y') == {'enddate': datetime(2013, 2, 28, 0, 0),
                                                           'date': datetime(2013, 2, 1, 0, 0), 'nondate': None}
        assert parse_date_or_range('2013') == {'enddate': datetime(2013, 12, 31, 0, 0),
                                               'date': datetime(2013, 1, 1, 0, 0), 'nondate': None}
        assert parse_date_or_range('2013', '%Y') == {'enddate': datetime(2013, 12, 31, 0, 0),
                                                     'date': datetime(2013, 1, 1, 0, 0), 'nondate': None}
        assert parse_date_or_range('date is 02/2013 for this test', fuzzy=True) == {
            'enddate': datetime(2013, 2, 28, 0, 0), 'date': datetime(2013, 2, 1, 0, 0),
            'nondate': ('date is ', ' for this test')}
        with pytest.raises(ValueError):
            parse_date_or_range('20/02')
        with pytest.raises(ValueError):
            parse_date_or_range('02/20')
        with pytest.raises(ValueError):
            parse_date_or_range('20/02', '%d/%m')

    def test_parse_date(self):
        assert parse_date('20/02/2013') == datetime(2013, 2, 20, 0, 0)
        assert parse_date('20/02/2013', '%d/%m/%Y') == datetime(2013, 2, 20, 0, 0)
        with pytest.raises(ValueError):
            parse_date('02/2013')
        with pytest.raises(ValueError):
            parse_date('02/2013', '%m/%Y')
