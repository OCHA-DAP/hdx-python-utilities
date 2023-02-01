"""Date parsing utilities."""
import time
from calendar import monthrange
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

import dateutil
from dateutil.parser import ParserError, _timelex, parserinfo

default_sd_year = 1
default_date_notz = datetime(
    year=default_sd_year,
    month=1,
    day=1,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
)
default_date = datetime(
    year=default_sd_year,
    month=1,
    day=1,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
    tzinfo=timezone.utc,
)
default_ed_year = 9990
default_enddate_notz = datetime(
    year=default_ed_year,
    month=12,
    day=31,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
)
default_enddate = datetime(
    year=default_ed_year,
    month=12,
    day=31,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
    tzinfo=timezone.utc,
)

# Used https://stackoverflow.com/questions/1703546/parsing-date-time-string-with-timezone-abbreviated-name-in-python/4766400#4766400
# with IST added
default_timezone_info = """-12 Y
-11 X NUT SST
-10 W CKT HAST HST TAHT TKT
-9 V AKST GAMT GIT HADT HNY
-8 U AKDT CIST HAY HNP PST PT
-7 T HAP HNR MST PDT
-6 S CST EAST GALT HAR HNC MDT
-5 R CDT COT EASST ECT EST ET HAC HNE PET
-4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
-3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
-2 O BRST FNT PMDT UYST WGST
-1 N AZOT CVT EGT
0 Z EGST GMT UTC WET WT
1 A CET DFT WAT WEDT WEST
2 B CAT CEDT CEST EET SAST WAST
3 C EAT EEDT EEST IDT MSK
4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
10 K AEST ChST PGT VLAT YAKST YAPT
11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
13 FJST NZDT
11.5 NFT
10.5 ACDT LHST
9.5 ACST
6.5 CCT MMT
5.75 NPT
5.5 IST SLT
4.5 AFT IRDT
3.5 IRST
-2.5 HAT NDT
-3.5 HNT NST NT
-4.5 HLV VET
-9.5 MART MIT"""


def get_tzinfos(timezone_info: str) -> Dict[str, int]:
    """Get tzinfos dictionary used by dateutil from timezone information
    string.

    Args:
        timezone_info (str): Timezones information string

    Returns:
        Dict[str, int]: tzinfos dictionary
    """
    tzinfos = {}
    for tz_descr in map(str.split, timezone_info.split("\n")):
        tz_offset = int(float(tz_descr[0]) * 3600)
        for tz_code in tz_descr[1:]:
            tzinfos[tz_code] = tz_offset
    return tzinfos


default_tzinfos = get_tzinfos(default_timezone_info)


# Ugly copy and paste from dateutil.parser._parser._ymd with dayfirst modified to mean day is outer value
# ie. dayfirst prefers dmy or ymd where in dateutil it prefers dmy and ydm!
class _ymd(list):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.century_specified = False
        self.dstridx = None
        self.mstridx = None
        self.ystridx = None

    @property
    def has_year(self):
        return self.ystridx is not None

    @property
    def has_month(self):
        return self.mstridx is not None

    @property
    def has_day(self):
        return self.dstridx is not None

    def could_be_day(self, value):
        if self.has_day:
            return False
        elif not self.has_month:
            return 1 <= value <= 31
        elif not self.has_year:
            # Be permissive, assume leap year
            month = self[self.mstridx]
            return 1 <= value <= monthrange(2000, month)[1]
        else:
            month = self[self.mstridx]
            year = self[self.ystridx]
            return 1 <= value <= monthrange(year, month)[1]

    def append(self, val, label=None):
        if hasattr(val, "__len__"):
            if val.isdigit() and len(val) > 2:
                self.century_specified = True
                if label not in [None, "Y"]:  # pragma: no cover
                    raise ValueError(label)
                label = "Y"
        elif val > 100:
            self.century_specified = True
            if label not in [None, "Y"]:  # pragma: no cover
                raise ValueError(label)
            label = "Y"

        super(self.__class__, self).append(int(val))

        if label == "M":
            if self.has_month:
                raise ValueError("Month is already set")
            self.mstridx = len(self) - 1
        elif label == "D":
            if self.has_day:
                raise ValueError("Day is already set")
            self.dstridx = len(self) - 1
        elif label == "Y":
            if self.has_year:
                raise ValueError("Year is already set")
            self.ystridx = len(self) - 1

    def _resolve_from_stridxs(self, strids):
        """Try to resolve the identities of year/month/day elements using
        ystridx, mstridx, and dstridx, if enough of these are specified."""
        if len(self) == 3 and len(strids) == 2:
            # we can back out the remaining stridx value
            missing = [x for x in range(3) if x not in strids.values()]
            key = [x for x in ["y", "m", "d"] if x not in strids]
            assert len(missing) == len(key) == 1
            key = key[0]
            val = missing[0]
            strids[key] = val

        assert len(self) == len(strids)  # otherwise this should not be called
        out = {key: self[strids[key]] for key in strids}
        return (out.get("y"), out.get("m"), out.get("d"))

    def resolve_ymd(self, yearfirst, dayfirst):
        len_ymd = len(self)
        year, month, day = (None, None, None)

        strids = (
            ("y", self.ystridx),
            ("m", self.mstridx),
            ("d", self.dstridx),
        )

        strids = {key: val for key, val in strids if val is not None}
        if len(self) == len(strids) > 0 or (
            len(self) == 3 and len(strids) == 2
        ):
            return self._resolve_from_stridxs(strids)

        mstridx = self.mstridx

        if len_ymd > 3:
            raise ValueError("More than three YMD values")
        elif len_ymd == 1 or (mstridx is not None and len_ymd == 2):
            # One member, or two members with a month string
            if mstridx is not None:
                month = self[mstridx]
                # since mstridx is 0 or 1, self[mstridx-1] always
                # looks up the other element
                other = self[mstridx - 1]
            else:
                other = self[0]

            if len_ymd > 1 or mstridx is None:
                if other > 31:
                    year = other
                else:
                    day = other

        elif len_ymd == 2:
            # Two members with numbers
            if self[0] > 31:
                # 99-01
                year, month = self
            elif self[1] > 31:
                # 01-99
                month, year = self
            elif dayfirst and self[1] <= 12:
                # 13-01
                day, month = self
            else:
                # 01-13
                month, day = self

        elif len_ymd == 3:
            # Three members
            if mstridx == 0:
                if self[1] > 31:
                    # Apr-2003-25
                    month, year, day = self
                else:
                    month, day, year = self
            elif mstridx == 1:
                if self[0] > 31 or (yearfirst and self[2] <= 31):
                    # 99-Jan-01
                    year, month, day = self
                else:
                    # 01-Jan-01
                    # Give precedence to day-first, since
                    # two-digit years is usually hand-written.
                    day, month, year = self

            elif mstridx == 2:
                # WTF!?
                if self[1] > 31:
                    # 01-99-Jan
                    day, year, month = self
                else:
                    # 99-01-Jan
                    year, day, month = self

            else:
                if (
                    self[0] > 31
                    or self.ystridx == 0
                    or (yearfirst and self[1] <= 12 and self[2] <= 31)
                ):
                    # 99-01-01
                    if dayfirst and self[1] <= 12:  # CHANGED
                        year, month, day = self
                    else:
                        year, day, month = self
                elif self[0] > 12 or (dayfirst and self[1] <= 12):
                    # 13-01-01
                    day, month, year = self
                else:
                    # 01-13-01
                    month, day, year = self

        return year, month, day


# Ugly copy and paste from dateutil.dateparser with minor changes
class DateParser(dateutil.parser.parser):  # pragma: no cover
    def _parse(
        self,
        timestr,
        dayfirst=None,
        yearfirst=None,
        fuzzy=False,
        fuzzy_with_tokens=False,
    ):
        """Private method which performs the heavy lifting of parsing, called
        from ``parse()``, which passes on its ``kwargs`` to this function.

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
        l = _timelex.split(timestr)  # noqa: E741

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
                    ymd.append(value, "M")

                    if i + 1 < len_l:
                        if l[i + 1] in ("-", "/"):
                            # Jan-01[-99]
                            sep = l[i + 1]
                            ymd.append(l[i + 2])

                            if i + 3 < len_l and l[i + 3] == sep:
                                # Jan-01-99
                                ymd.append(l[i + 4])
                                i += 2

                            i += 2

                        elif (
                            i + 4 < len_l
                            and l[i + 1] == l[i + 3] == " "
                            and info.pertain(l[i + 2])
                        ):
                            # Jan of 01
                            # In this case, 01 is clearly year
                            if l[i + 4].isdigit():
                                # Convert it here to become unambiguous
                                value = int(l[i + 4])
                                year = str(info.convertyear(value))
                                ymd.append(year, "Y")
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
                elif self._could_be_tzname(
                    res.hour, res.tzname, res.tzoffset, l[i]
                ):
                    res.tzname = l[i]
                    res.tzoffset = info.tzoffset(res.tzname)

                    # Check for something like GMT+3, or BRST+3. Notice
                    # that it doesn't mean "I am 3 hours after GMT", but
                    # "my time +3 is GMT". If found, we reverse the
                    # logic so that timezone parsing code will get it
                    # right.
                    if i + 1 < len_l and l[i + 1] in ("+", "-"):
                        l[i + 1] = ("+", "-")[l[i + 1] == "+"]
                        res.tzoffset = None
                        if info.utczone(res.tzname):
                            # With something like GMT+3, the timezone
                            # is *not* GMT.
                            res.tzname = None

                # Check for a numbered timezone
                elif res.hour is not None and l[i] in ("+", "-"):
                    signal = (-1, 1)[l[i] == "+"]
                    len_li = len(l[i + 1])

                    # TODO: check that l[i + 1] is integer?
                    if len_li == 4:
                        # -0300
                        hour_offset = int(l[i + 1][:2])
                        min_offset = int(l[i + 1][2:])
                    elif i + 2 < len_l and l[i + 2] == ":":
                        # -03:00
                        hour_offset = int(l[i + 1])
                        min_offset = int(
                            l[i + 3]
                        )  # TODO: Check that l[i+3] is minute-like?
                        i += 2
                    elif len_li <= 2:
                        # -[0]3
                        hour_offset = int(l[i + 1][:2])
                        min_offset = 0
                    else:
                        raise ValueError(timestr)

                    res.tzoffset = signal * (
                        hour_offset * 3600 + min_offset * 60
                    )

                    # Look for a timezone name between parenthesis
                    if (
                        i + 5 < len_l
                        and info.jump(l[i + 2])
                        and l[i + 3] == "("
                        and l[i + 5] == ")"
                        and 3 <= len(l[i + 4])
                        and self._could_be_tzname(
                            res.hour, res.tzname, None, l[i + 4]
                        )
                    ):
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
        # *** CHANGES FROM HERE DOWN TO 3 VALUES IN TUPLE ***
        except (IndexError, ValueError):
            return None, None, None

        if not info.validate(res):
            return None, None, None

        if fuzzy_with_tokens:
            skipped_tokens, date_tokens = self._recombine_skipped_date(
                l, skipped_idxs
            )
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
                if prev is None or prev == "date":
                    skipped_tokens.append(token)
                else:
                    skipped_tokens[-1] = skipped_tokens[-1] + token
                prev = "skipped"
            else:
                if prev is None or prev == "skipped":
                    date_tokens.append(token)
                else:
                    date_tokens[-1] = date_tokens[-1] + token
                prev = "date"

        return skipped_tokens, date_tokens


DEFAULTPARSER = DateParser(parserinfo(dayfirst=True))


def parse(
    timestr, default=None, ignoretz=False, tzinfos=None, **kwargs
):  # pragma: no cover
    """Parse the date/time string into a :class:`datetime.datetime` object.

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
        default = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    res, skipped_tokens, date_tokens = DEFAULTPARSER._parse(timestr, **kwargs)

    if res is None:
        raise ParserError("Unknown string format: %s", timestr)

    if len(res) == 0:
        raise ParserError("String does not contain a date: %s", timestr)

    try:
        ret = DEFAULTPARSER._build_naive(res, default)
    except ValueError as e:
        raise ParserError(str(e) + f": {timestr}") from e

    if not ignoretz:
        ret = DEFAULTPARSER._build_tzaware(ret, res, tzinfos)

    if kwargs.get("fuzzy_with_tokens", False):
        return ret, skipped_tokens, date_tokens
    else:
        return ret


def now_utc() -> datetime:
    """Return now with UTC timezone.

    Returns:
        datetime: Now with UTC timezone
    """
    return datetime.now(timezone.utc)


def parse_date_range(
    string: str,
    date_format: Optional[str] = None,
    timezone_handling: int = 0,
    fuzzy: Optional[Dict] = None,
    include_microseconds: bool = False,
    zero_time: bool = False,
    max_starttime: bool = False,
    max_endtime: bool = False,
    default_timezones: Optional[str] = None,
) -> Tuple[datetime, datetime]:
    """Parse date from string using specified date_format if given and return
    datetime date range in dictionary keys startdate and enddate. If no
    date_format is supplied, the function will guess, which for unambiguous
    formats, should work fine.

    By default, no timezone information will be parsed and the returned datetime will
    have timezone UTC. To change this behaviour, timezone_handling should be changed
    from its default of 0. If it is 1, then no timezone information will be parsed and a
    naive datetime will be returned. If it is 2 or more, then timezone information will
    be parsed. For 2, failure to parse timezone will result in a naive datetime. For 3,
    failure to parse timezone will result in the timezone being set to UTC. For 4 and 5,
    the time will be converted from whatever timezone is identified to UTC. For 4,
    failure to parse timezone will result in a naive (local) datetime converted to UTC.
    For 5, failure to parse timezone will result in the timezone being set to UTC.

    To parse a date within a string containing other text, you can supply a dictionary
    in the fuzzy parameter. In this case, dateutil's fuzzy parsing is used and the
    results returned in the dictionary in keys startdate, enddate, date (the string
    elements used to make the date) and nondate (the non date part of the string).

    By default, microseconds are ignored (set to 0), but can be included by setting
    include_microseconds to True. Any time elements are set to 0 if zero_time is True.
    If max_starttime is True, then the start date's time is set to 23:59:59. If
    max_endtime is True, then the end date's time is set to 23:59:59.

    When inferring time zones, a default set of time zones will be used unless
    overridden by passing in default_timezones which is a string of the form:

        -11 X NUT SST
        -10 W CKT HAST HST TAHT TKT

    Args:
        string (str): Dataset date string
        date_format (Optional[str]): Date format. If None is given, will attempt to guess. Defaults to None.
        timezone_handling (int): Timezone handling. See description. Defaults to 0 (ignore timezone, return UTC).
        fuzzy (Optional[Dict]): If dict supplied, fuzzy matching will be used and results returned in dict
        include_microseconds (bool): Includes microseconds if True. Defaults to False.
        zero_time (bool): Zero time elements of datetime if True. Defaults to False.
        max_starttime (bool): Make start date time component 23:59:59:999999. Defaults to False.
        max_endtime (bool): Make end date time component 23:59:59:999999. Defaults to False.
        default_timezones (Optional[str]): Timezone information. Defaults to None. (Internal default).

    Returns:
        Tuple[datetime,datetime]: Tuple containing start date and end date
    """
    if date_format is None or fuzzy is not None:
        if timezone_handling >= 2:
            if default_timezones is None:
                tzinfos = default_tzinfos
            else:
                tzinfos = get_tzinfos(default_timezones)
            ignoretz = False
        else:
            ignoretz = True
            tzinfos = None

        if fuzzy is not None:
            parsed_string1 = parse(
                string,
                fuzzy_with_tokens=True,
                default=default_date_notz,
                ignoretz=ignoretz,
                tzinfos=tzinfos,
            )
            parsed_string2 = parse(
                string,
                fuzzy_with_tokens=True,
                default=default_enddate_notz,
                ignoretz=ignoretz,
                tzinfos=tzinfos,
            )
            startdate = parsed_string1[0]
            enddate = parsed_string2[0]
            nondate = parsed_string1[1]
            if nondate:
                fuzzy["nondate"] = nondate
            else:
                fuzzy["nondate"] = None
            fuzzy["date"] = parsed_string1[2]
        else:
            startdate = parse(
                string,
                default=default_date_notz,
                ignoretz=ignoretz,
                tzinfos=tzinfos,
            )
            enddate = parse(
                string,
                default=default_enddate_notz,
                ignoretz=ignoretz,
                tzinfos=tzinfos,
            )
        if (
            startdate.year == default_sd_year
            and enddate.year == default_ed_year
        ):
            raise ParserError("No year in date!")
    else:
        try:
            startdate = datetime.strptime(string, date_format)
        except ValueError as e:
            raise ParserError(str(e)) from e
        if (
            startdate.year == 1900 and "%Y" not in date_format
        ):  # 1900 is default when no year supplied
            raise ParserError("No year in date!")
        enddate = startdate
        if not any(x in date_format for x in ["%d", "%j"]):
            startdate = startdate.replace(day=default_date.day)
            endday = default_enddate.day
            not_set = True
            while not_set:
                try:
                    enddate = enddate.replace(day=endday)
                    not_set = False
                except ValueError as e:
                    endday -= 1
                    if endday == 0:
                        raise ParserError(
                            f"No end day of month found for {str(enddate)}!"
                        ) from e
        if not any(str in date_format for str in ["%b", "%B", "%m", "%j"]):
            startdate = startdate.replace(month=default_date.month)
            enddate = enddate.replace(month=default_enddate.month)
    if zero_time:
        if not max_starttime:
            startdate = startdate.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if not max_endtime:
            enddate = enddate.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
    if max_starttime:
        startdate = startdate.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
    if max_endtime:
        enddate = enddate.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
    if timezone_handling == 0:
        startdate = startdate.replace(tzinfo=timezone.utc)
        enddate = enddate.replace(tzinfo=timezone.utc)
    elif timezone_handling == 3:
        if startdate.tzinfo is None:
            startdate = startdate.replace(tzinfo=timezone.utc)
        if enddate.tzinfo is None:
            enddate = enddate.replace(tzinfo=timezone.utc)
    elif timezone_handling == 4:
        startdate = startdate.astimezone(timezone.utc)
        enddate = enddate.astimezone(timezone.utc)
    elif timezone_handling == 5:
        if startdate.tzinfo is None:
            startdate = startdate.replace(tzinfo=timezone.utc)
        else:
            startdate = startdate.astimezone(timezone.utc)
        if enddate.tzinfo is None:
            enddate = enddate.replace(tzinfo=timezone.utc)
        else:
            enddate = enddate.astimezone(timezone.utc)
    if not include_microseconds:
        startdate = startdate.replace(microsecond=0)
        enddate = enddate.replace(microsecond=0)
    if fuzzy is not None:
        fuzzy["startdate"] = startdate
        fuzzy["enddate"] = enddate
    return startdate, enddate


def parse_date(
    string: str,
    date_format: Optional[str] = None,
    timezone_handling: int = 0,
    fuzzy: Optional[Dict] = None,
    include_microseconds: bool = False,
    zero_time: bool = False,
    max_time: bool = False,
    default_timezones: Optional[str] = None,
) -> datetime:
    """Parse date from string using specified date_format and return a datetime
    object. Raises exception for dates that are missing year, month or day. If
    no date_format is supplied, the function will guess, which for unambiguous
    formats, should work fine.

    By default, no timezone information will be parsed and the returned datetime will
    have timezone UTC. To change this behaviour, timezone_handling should be changed
    from its default of 0. If it is 1, then no timezone information will be parsed and a
    naive datetime will be returned. If it is 2 or more, then timezone information will
    be parsed. For 2, failure to parse timezone will result in a naive datetime. For 3,
    failure to parse timezone will result in the timezone being set to UTC. For 4 and 5,
    the time will be converted from whatever timezone is identified to UTC. For 4,
    failure to parse timezone will result in a naive (local) datetime converted to UTC.
    For 5, failure to parse timezone will result in the timezone being set to UTC.

    To parse a date within a string containing other text, you can supply a dictionary
    in the fuzzy parameter. In this case, dateutil's fuzzy parsing is used and the
    results returned in the dictionary in keys startdate, enddate, date (the string
    elements used to make the date) and nondate (the non date part of the string).

    By default, microseconds are ignored (set to 0), but can be included by setting
    include_microseconds to True. Any time elements are set to 0 if zero_time is True.
    If max_starttime is True, then the start date's time is set to 23:59:59. If
    max_endtime is True, then the end date's time is set to 23:59:59.

    When inferring time zones, a default set of time zones will be used unless
    overridden by passing in default_timezones which is a string of the form:

        -11 X NUT SST
        -10 W CKT HAST HST TAHT TKT

    Args:
        string (str): Dataset date string
        date_format (Optional[str]): Date format. If None is given, will attempt to guess. Defaults to None.
        timezone_handling (int): Timezone handling. See description. Defaults to 0 (ignore timezone, return UTC).
        fuzzy (Optional[Dict]): If dict supplied, fuzzy matching will be used and results returned in dict
        include_microseconds (bool): Includes microseconds if True. Defaults to False.
        zero_time (bool): Zero time elements of datetime if True. Defaults to False.
        max_time (bool): Make date time component 23:59:59:999999. Defaults to False.
        default_timezones (Optional[str]): Timezone information. Defaults to None. (Internal default).

    Returns:
        datetime: The parsed date
    """
    if max_time:
        max_starttime = True
        max_endtime = True
        zero_time = False
    else:
        max_starttime = False
        max_endtime = False

    startdate, enddate = parse_date_range(
        string,
        date_format=date_format,
        timezone_handling=timezone_handling,
        fuzzy=fuzzy,
        include_microseconds=include_microseconds,
        zero_time=zero_time,
        max_starttime=max_starttime,
        max_endtime=max_endtime,
        default_timezones=default_timezones,
    )
    if startdate != enddate:
        raise ParserError("date is not a specific day!")
    return startdate


def get_timestamp_from_datetime(date: datetime) -> float:
    """Convert datetime to timestamp.

    Args:
        date (datetime): Date to convert

    Returns:
        float: Timestamp
    """
    if date.tzinfo is None:
        return (
            time.mktime(
                (
                    date.year,
                    date.month,
                    date.day,
                    date.hour,
                    date.minute,
                    date.second,
                    -1,
                    -1,
                    -1,
                )
            )
            + date.microsecond / 1e6
        )
    else:
        return (
            date - datetime(1970, 1, 1, tzinfo=timezone.utc)
        ).total_seconds()


def get_datetime_from_timestamp(
    timestamp: float,
    timezone: datetime.tzinfo = timezone.utc,
    today: datetime = now_utc(),
) -> datetime:
    """Convert timestamp to datetime.

    Args:
        timestamp (float): Timestamp to convert
        timezone (datetime.tzinfo): Timezone to use
        today (datetime): Today's date. Defaults to now_utc.

    Returns:
        datetime: Date of timestamp
    """
    if timestamp > get_timestamp_from_datetime(today):
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone)
