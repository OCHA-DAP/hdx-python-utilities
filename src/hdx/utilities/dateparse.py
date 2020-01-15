# -*- coding: utf-8 -*-
"""Date parsing utilities"""
from datetime import datetime
from typing import Optional, Dict, Tuple

from dateutil import parser

default_sd_year = 1
default_date = datetime(year=default_sd_year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
default_ed_year = 9990
default_enddate = datetime(year=default_ed_year, month=12, day=31, hour=0, minute=0, second=0, microsecond=0)


def parse_date_range(string, date_format=None, fuzzy=None):
    # type: (str, Optional[str], Optional[Dict]) -> Tuple[datetime,datetime]
    """Parse date (dropping any time elements) from string using specified format. If no format is supplied, the
    function will guess. For unambiguous formats, this should be fine. Returns date range in dictionary keys
    startdate and enddate. If a dictionary is supplied in the fuzzy parameter, then dateutil's fuzzy parsing is
    used and the results returned in the dictionary in keys startdate, enddate and nondate (the non date part of
    the string).

    Args:
        string (str): Dataset date string
        date_format (Optional[str]): Date format. If None is given, will attempt to guess. Defaults to None.
        fuzzy (Optional[Dict]): If dict supplied, fuzzy matching will be used and results returned in dict

    Returns:
        Tuple[datetime,datetime]: Tuple containing start date and end date
    """
    if date_format is None or fuzzy is not None:
        if fuzzy is not None:
            parsed_string1 = parser.parse(string, fuzzy_with_tokens=True, default=default_date)
            parsed_string2 = parser.parse(string, fuzzy_with_tokens=True, default=default_enddate)
            startdate = parsed_string1[0]
            enddate = parsed_string2[0]
            nondate = parsed_string1[1]
            if nondate:
                fuzzy['nondate'] = nondate
            else:
                fuzzy['nondate'] = None
            datestr = parsed_string1[2]
            if datestr:
                fuzzy['date'] = datestr
            else:
                fuzzy['date'] = None
        else:
            startdate = parser.parse(string, default=default_date)
            enddate = parser.parse(string, default=default_enddate)
        if startdate.year == default_sd_year and enddate.year == default_ed_year:
            raise ValueError('No year in date!')
    else:
        startdate = datetime.strptime(string, date_format)
        if startdate.year == 1900 and '%Y' not in date_format:  # 1900 is default when no year supplied
            raise ValueError('No year in date!')
        enddate = startdate
        if not any(str in date_format for str in ['%d', '%j']):
            startdate = startdate.replace(day=default_date.day)
            endday = default_enddate.day
            not_set = True
            while not_set:
                try:
                    enddate = enddate.replace(day=endday)
                    not_set = False
                except ValueError:
                    endday -= 1
                    if endday == 0:
                        raise
        if not any(str in date_format for str in ['%b', '%B', '%m', '%j']):
            startdate = startdate.replace(month=default_date.month)
            enddate = enddate.replace(month=default_enddate.month)
    startdate = startdate.replace(hour=0, minute=0, second=0, microsecond=0)
    enddate = enddate.replace(hour=0, minute=0, second=0, microsecond=0)
    if fuzzy is not None:
        fuzzy['startdate'] = startdate
        fuzzy['enddate'] = enddate
    return startdate, enddate


def parse_date(string, date_format=None):
    # type: (str, Optional[str]) -> datetime
    """Parse date (dropping any time elements) from string using specified format. If no format is supplied, the
    function will guess. For unambiguous formats, this should be fine. Returns a datetime object. Raises exception for
    dates that are missing year, month or day.

    Args:
        string (str): Dataset date string
        date_format (Optional[str]): Date format. If None is given, will attempt to guess. Defaults to None.

    Returns:
        datetime: The parsed date
    """
    startdate, enddate = parse_date_range(string, date_format=date_format)
    if startdate != enddate:
        raise ValueError('date is not a specific day!')
    return startdate
