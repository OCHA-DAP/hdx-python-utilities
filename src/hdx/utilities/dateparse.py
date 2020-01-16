# -*- coding: utf-8 -*-
"""Date parsing utilities"""
from datetime import datetime
from parser import ParserError
from typing import Optional, Dict, Tuple

import dateutil
from dateutil.parser import _timelex
from dateutil.parser._parser import _ymd

default_sd_year = 1
default_date = datetime(year=default_sd_year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
default_ed_year = 9990
default_enddate = datetime(year=default_ed_year, month=12, day=31, hour=0, minute=0, second=0, microsecond=0)


# Ugly copy and paste from dateutil.dateparser with minor changes
class DateParser(dateutil.parser.parser):
    def _parse(self, timestr, dayfirst=None, yearfirst=None, fuzzy=False,
               fuzzy_with_tokens=False):
        """
        Private method which performs the heavy lifting of parsing, called from
        ``parse()``, which passes on its ``kwargs`` to this function.

        :param timestr:
            The string to parse.

        :param dayfirst:
            Whether to interpret the first value in an ambiguous 3-integer date
            (e.g. 01/05/09) as the day (``True``) or month (``False``). If
            ``yearfirst`` is set to ``True``, this distinguishes between YDM
            and YMD. If set to ``None``, this value is retrieved from the
            current :class:`parserinfo` object (which itself defaults to
            ``False``).

        :param yearfirst:
            Whether to interpret the first value in an ambiguous 3-integer date
            (e.g. 01/05/09) as the year. If ``True``, the first number is taken
            to be the year, otherwise the last number is taken to be the year.
            If this is set to ``None``, the value is retrieved from the current
            :class:`parserinfo` object (which itself defaults to ``False``).

        :param fuzzy:
            Whether to allow fuzzy parsing, allowing for string like "Today is
            January 1, 2047 at 8:21:00AM".

        :param fuzzy_with_tokens:
            If ``True``, ``fuzzy`` is automatically set to True, and the parser
            will return a tuple where the first element is the parsed
            :class:`datetime.datetime` datetimestamp and the second element is
            a tuple containing the portions of the string which were ignored:

            .. doctest::

                >>> from dateutil.parser import parse
                >>> parse("Today is January 1, 2047 at 8:21:00AM", fuzzy_with_tokens=True)
                (datetime.datetime(2047, 1, 1, 8, 21), (u'Today is ', u' ', u'at '))

        """
        if fuzzy_with_tokens:
            fuzzy = True

        info = self.info

        if dayfirst is None:
            dayfirst = info.dayfirst

        if yearfirst is None:
            yearfirst = info.yearfirst

        res = self._result()
        l = _timelex.split(timestr)  # Splits the timestr into tokens

        skipped_idxs = []

        # year/month/day list
        ymd = _ymd()

        len_l = len(l)
        i = 0
        try:
            while i < len_l:

                # Check if it's a number
                value_repr = l[i]
                try:
                    value = float(value_repr)
                except ValueError:
                    value = None

                if value is not None:
                    # Numeric token
                    i = self._parse_numeric_token(l, i, info, ymd, res, fuzzy)

                # Check weekday
                elif info.weekday(l[i]) is not None:
                    value = info.weekday(l[i])
                    res.weekday = value

                # Check month name
                elif info.month(l[i]) is not None:
                    value = info.month(l[i])
                    ymd.append(value, 'M')

                    if i + 1 < len_l:
                        if l[i + 1] in ('-', '/'):
                            # Jan-01[-99]
                            sep = l[i + 1]
                            ymd.append(l[i + 2])

                            if i + 3 < len_l and l[i + 3] == sep:
                                # Jan-01-99
                                ymd.append(l[i + 4])
                                i += 2

                            i += 2

                        elif (i + 4 < len_l and l[i + 1] == l[i + 3] == ' ' and
                              info.pertain(l[i + 2])):
                            # Jan of 01
                            # In this case, 01 is clearly year
                            if l[i + 4].isdigit():
                                # Convert it here to become unambiguous
                                value = int(l[i + 4])
                                year = str(info.convertyear(value))
                                ymd.append(year, 'Y')
                            else:
                                # Wrong guess
                                pass
                                # TODO: not hit in tests
                            i += 4

                # Check am/pm
                elif info.ampm(l[i]) is not None:
                    value = info.ampm(l[i])
                    val_is_ampm = self._ampm_valid(res.hour, res.ampm, fuzzy)

                    if val_is_ampm:
                        res.hour = self._adjust_ampm(res.hour, value)
                        res.ampm = value

                    elif fuzzy:
                        skipped_idxs.append(i)

                # Check for a timezone name
                elif self._could_be_tzname(res.hour, res.tzname, res.tzoffset, l[i]):
                    res.tzname = l[i]
                    res.tzoffset = info.tzoffset(res.tzname)

                    # Check for something like GMT+3, or BRST+3. Notice
                    # that it doesn't mean "I am 3 hours after GMT", but
                    # "my time +3 is GMT". If found, we reverse the
                    # logic so that timezone parsing code will get it
                    # right.
                    if i + 1 < len_l and l[i + 1] in ('+', '-'):
                        l[i + 1] = ('+', '-')[l[i + 1] == '+']
                        res.tzoffset = None
                        if info.utczone(res.tzname):
                            # With something like GMT+3, the timezone
                            # is *not* GMT.
                            res.tzname = None

                # Check for a numbered timezone
                elif res.hour is not None and l[i] in ('+', '-'):
                    signal = (-1, 1)[l[i] == '+']
                    len_li = len(l[i + 1])

                    # TODO: check that l[i + 1] is integer?
                    if len_li == 4:
                        # -0300
                        hour_offset = int(l[i + 1][:2])
                        min_offset = int(l[i + 1][2:])
                    elif i + 2 < len_l and l[i + 2] == ':':
                        # -03:00
                        hour_offset = int(l[i + 1])
                        min_offset = int(l[i + 3])  # TODO: Check that l[i+3] is minute-like?
                        i += 2
                    elif len_li <= 2:
                        # -[0]3
                        hour_offset = int(l[i + 1][:2])
                        min_offset = 0
                    else:
                        raise ValueError(timestr)

                    res.tzoffset = signal * (hour_offset * 3600 + min_offset * 60)

                    # Look for a timezone name between parenthesis
                    if (i + 5 < len_l and
                            info.jump(l[i + 2]) and l[i + 3] == '(' and
                            l[i + 5] == ')' and
                            3 <= len(l[i + 4]) and
                            self._could_be_tzname(res.hour, res.tzname,
                                                  None, l[i + 4])):
                        # -0300 (BRST)
                        res.tzname = l[i + 4]
                        i += 4

                    i += 1

                # Check jumps
                elif not (info.jump(l[i]) or fuzzy):
                    raise ValueError(timestr)

                else:
                    skipped_idxs.append(i)
                i += 1

            # Process year/month/day
            year, month, day = ymd.resolve_ymd(yearfirst, dayfirst)

            res.century_specified = ymd.century_specified
            res.year = year
            res.month = month
            res.day = day

        except (IndexError, ValueError):
            return None, None, None

        if not info.validate(res):
            return None, None, None

        if fuzzy_with_tokens:
            skipped_tokens, date_tokens = self._recombine_skipped_date(l, skipped_idxs)
            return res, tuple(skipped_tokens), tuple(date_tokens)
        else:
            return res, None, None

    def _recombine_skipped_date(self, tokens, skipped_idxs):
        """
        >>> tokens = ["foo", " ", "bar", " ", "19June2000", "baz"]
        >>> skipped_idxs = [0, 1, 2, 5]
        >>> _recombine_skipped_date(tokens, skipped_idxs)
        ["foo bar", "baz"], ["19June2000"]
        """
        skipped_tokens = []
        date_tokens = []
        prev = None
        for idx, token in enumerate(tokens):
            if idx in skipped_idxs:
                if prev is None or prev == 'date':
                    skipped_tokens.append(token)
                else:
                    skipped_tokens[-1] = skipped_tokens[-1] + token
                prev = 'skipped'
            else:
                if prev is None or prev == 'skipped':
                    date_tokens.append(token)
                else:
                    date_tokens[-1] = date_tokens[-1] + token
                prev = 'date'

        return skipped_tokens, date_tokens


DEFAULTPARSER = DateParser()


def parse(timestr, default=None,
          ignoretz=False, tzinfos=None, **kwargs):
    """
    Parse the date/time string into a :class:`datetime.datetime` object.

    :param timestr:
        Any date/time string using the supported formats.

    :param default:
        The default datetime object, if this is a datetime object and not
        ``None``, elements specified in ``timestr`` replace elements in the
        default object.

    :param ignoretz:
        If set ``True``, time zones in parsed strings are ignored and a
        naive :class:`datetime.datetime` object is returned.

    :param tzinfos:
        Additional time zone names / aliases which may be present in the
        string. This argument maps time zone names (and optionally offsets
        from those time zones) to time zones. This parameter can be a
        dictionary with timezone aliases mapping time zone names to time
        zones or a function taking two parameters (``tzname`` and
        ``tzoffset``) and returning a time zone.

        The timezones to which the names are mapped can be an integer
        offset from UTC in seconds or a :class:`tzinfo` object.

        .. doctest::
           :options: +NORMALIZE_WHITESPACE

            >>> from dateutil.parser import parse
            >>> from dateutil.tz import gettz
            >>> tzinfos = {"BRST": -7200, "CST": gettz("America/Chicago")}
            >>> parse("2012-01-19 17:21:00 BRST", tzinfos=tzinfos)
            datetime.datetime(2012, 1, 19, 17, 21, tzinfo=tzoffset(u'BRST', -7200))
            >>> parse("2012-01-19 17:21:00 CST", tzinfos=tzinfos)
            datetime.datetime(2012, 1, 19, 17, 21,
                              tzinfo=tzfile('/usr/share/zoneinfo/America/Chicago'))

        This parameter is ignored if ``ignoretz`` is set.

    :param \\*\\*kwargs:
        Keyword arguments as passed to ``_parse()``.

    :return:
        Returns a :class:`datetime.datetime` object or, if the
        ``fuzzy_with_tokens`` option is ``True``, returns a tuple, the
        first element being a :class:`datetime.datetime` object, the second
        a tuple containing the fuzzy tokens.

    :raises ParserError:
        Raised for invalid or unknown string format, if the provided
        :class:`tzinfo` is not in a valid format, or if an invalid date
        would be created.

    :raises TypeError:
        Raised for non-string or character stream input.

    :raises OverflowError:
        Raised if the parsed date exceeds the largest valid C integer on
        your system.
    """

    if default is None:
        default = datetime.now().replace(hour=0, minute=0,
                                         second=0, microsecond=0)

    res, skipped_tokens, date_tokens = DEFAULTPARSER._parse(timestr, **kwargs)

    if res is None:
        raise ParserError("Unknown string format: %s", timestr)

    if len(res) == 0:
        raise ParserError("String does not contain a date: %s", timestr)

    ret = DEFAULTPARSER._build_naive(res, default)

    if not ignoretz:
        ret = DEFAULTPARSER._build_tzaware(ret, res, tzinfos)

    if kwargs.get('fuzzy_with_tokens', False):
        return ret, skipped_tokens, date_tokens
    else:
        return ret


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
            parsed_string1 = parse(string, fuzzy_with_tokens=True, default=default_date)
            parsed_string2 = parse(string, fuzzy_with_tokens=True, default=default_enddate)
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
            startdate = parse(string, default=default_date)
            enddate = parse(string, default=default_enddate)
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
