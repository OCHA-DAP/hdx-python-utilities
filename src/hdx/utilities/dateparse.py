# -*- coding: utf-8 -*-
"""Date parsing utilities"""
from datetime import datetime
from typing import Optional, Dict, Any

from dateutil import parser

default_sd_year = 1
default_date = datetime(year=default_sd_year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
default_ed_year = 9999
default_enddate = datetime(year=default_ed_year, month=12, day=31, hour=0, minute=0, second=0, microsecond=0)


def parse_date(string, date_format=None, allow_range=True, fuzzy=False):
    # type: (str, Optional[str], bool, bool) -> Dict[str,Any]
    """Parse date (dropping any time elements) from string using specified format. If no format is supplied, the
    function will guess. For unambiguous formats, this should be fine. Returns date in a dictionary key
    date. If allow_range is False or month and day are both provided, enddate will be None. If fuzzy is True,
    then dateutil's fuzzy parsing is used with the non date part of the string returned in key nondate.

    Args:
        string (str): Dataset date string
        date_format (Optional[str]): Date format. If None is given, will attempt to guess. Defaults to None.
        allow_range (bool): Whether to allow date to be a range. Defaults to True.
        fuzzy (bool): Whether to use fuzzy matching and return nondate part of string. Defaults to False.

    Returns:
        Dict[str,Any]: Dictionary containing start date and end date (and nondate if fuzzy is True)
    """
    datedict = dict()
    if date_format is None or fuzzy:
        if fuzzy:
            parsed_string1 = parser.parse(string, fuzzy_with_tokens=True, default=default_date)
            parsed_string2 = parser.parse(string, fuzzy_with_tokens=True, default=default_enddate)
            date = parsed_string1[0]
            enddate = parsed_string2[0]
            nondate = parsed_string1[1]
            if nondate:
                datedict['nondate'] = nondate
        else:
            date = parser.parse(string, default=default_date)
            enddate = parser.parse(string, default=default_enddate)
        if date.year == default_sd_year and enddate.year == default_ed_year:
            raise ValueError('No year in date!')
    else:
        date = datetime.strptime(string, date_format)
        if date.year == 1900 and '%Y' not in date_format:  # 1900 is default when no year supplied
            raise ValueError('No year in date!')
        enddate = date
        if not any(str in date_format for str in ['%d', '%j']):
            date = date.replace(day=default_date.day)
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
            date = date.replace(month=default_date.month)
            enddate = enddate.replace(month=default_enddate.month)
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    enddate = enddate.replace(hour=0, minute=0, second=0, microsecond=0)
    if allow_range is False:
        if date == enddate:
            enddate = None
        else:
            raise ValueError('allow_range is False and date is a range!')
    elif date == enddate:
        enddate = None
    datedict['date'] = date
    datedict['enddate'] = enddate
    return datedict
