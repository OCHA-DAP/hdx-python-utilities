# -*- coding: utf-8 -*-
"""Location utilities"""
import logging
from typing import List, Callable, Tuple, Optional, TypeVar, Any

from hdx.utilities.downloader import Download, DownloadError
from hdx.utilities.loader import load_json
from hdx.utilities.path import script_dir_plus_file

ExceptionUpperBound = TypeVar('T', bound='Exception')


logger = logging.getLogger(__name__)


class Location(object):
    """Location class with various methods to help with countries and regions. Uses World Bank API unless countries
    argument supplied with list of dicts of form::
        {'id': 'AFG', 'iso2Code': 'AF', 'name': 'Afghanistan',
        'latitude': '34.5228', 'longitude': '69.1761',
        'region': {'value': 'South Asia', 'id': 'SAS'},
        'adminregion': {'value': 'South Asia', 'id': 'SAS'},
        'capitalCity': 'Kabul',
        'lendingType': {'value': 'IDA', 'id': 'IDX'},
        'incomeLevel': {'value': 'Low income', 'id': 'LIC'}}

    Args:
        countries (Optional[List]): List of countries in same format as World Bank API. Defaults to None.
        url (Optional[str]): URL of World Bank API. Defaults to 'http://api.worldbank.org/countries?format=json&per_page=10000'.
    """

    def __init__(self, countries=None, url='http://api.worldbank.org/countries?format=json&per_page=10000'):
        # type: (Optional[List]) -> None
        if countries is None:
            json = None
            if url is not None:
                try:
                    response = Download().download(url)
                    json = response.json()
                except DownloadError:
                    logger.exception('Download from API failed! Falling back to stored countries file.')
            if json is None:
                json = load_json(script_dir_plus_file('countries.json', Location))
            countries = json[1]
        self.countries = dict()
        self.iso2iso3 = dict()
        self.countrynames2iso3 = dict()
        self.regions2countries = dict()
        self.regionids2names = dict()
        self.regionnames2ids = dict()
        for country in countries:
            if country['region']['value'] != 'Aggregates':
                iso2 = country['iso2Code'].upper()
                iso3 = country['id'].upper()
                countryname = country['name']
                regionid = country['region']['id']
                regionname = country['region']['value']
                self.countries[iso3] = country
                self.iso2iso3[iso2] = iso3
                self.countrynames2iso3[countryname.upper()] = iso3
                region = self.regions2countries.get(regionid)
                if region is None:
                    region = set()
                    self.regions2countries[regionid] = region
                region.add(iso3)
                self.regionids2names[regionid] = regionname
                self.regionnames2ids[regionname.upper()] = regionid
        for regionid in self.regions2countries:
            self.regions2countries[regionid] = sorted(list(self.regions2countries[regionid]))

    def get_country_info_from_iso3(self, iso3, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[Dict[str]]
        """Get country information from iso3 code

        Args:
            iso3 (str): Iso 3 code for which to get country name
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[Dict[str]]: country information
        """
        country = self.countries.get(iso3.upper())
        if country is not None:
            return country

        if exception is not None:
            raise exception
        return None

    def get_country_name_from_iso3(self, iso3, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[str]
        """Get country name from iso3 code

        Args:
            iso3 (str): Iso 3 code for which to get country name
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[str]: country name
        """
        countryinfo = self.get_country_info_from_iso3(iso3, exception)
        if countryinfo is not None:
            return countryinfo['name']
        return None

    def get_iso3_from_iso2(self, iso2, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[str]
        """Get iso3 from iso2 code

        Args:
            iso2 (str): Iso 2 code for which to get country name
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[str]: Iso 3 code
        """
        iso3 = self.iso2iso3.get(iso2.upper())
        if iso3 is not None:
            return iso3

        if exception is not None:
            raise exception
        return None

    def get_country_info_from_iso2(self, iso2, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[Dict[str]]
        """Get country name from iso2 code

        Args:
            iso2 (str): Iso 2 code for which to get country name
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[Dict[str]]: country information
        """
        iso3 = self.get_iso3_from_iso2(iso2, exception)
        if iso3 is not None:
            return self.get_country_info_from_iso3(iso3, exception)
        return None

    def get_country_name_from_iso2(self, iso2, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[str]
        """Get country name from iso2 code

        Args:
            iso2 (str): Iso 2 code for which to get country name
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[str]: country name
        """
        iso3 = self.get_iso3_from_iso2(iso2, exception)
        if iso3 is not None:
            return self.get_country_name_from_iso3(iso3, exception)
        return None

    def get_iso3_country_code(self, country, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Optional[str]]
        """Get iso 3 code for country. Only exact matches or None are returned.

        Args:
            country (str): Country for which to get iso 3 code
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Optional[str]: Return iso 3 country code or None
        """
        countryupper = country.upper()
        len_countryupper = len(countryupper)
        if len_countryupper == 3:
            if countryupper in self.countries:
                return countryupper
        elif len_countryupper == 2:
            iso3 = self.iso2iso3.get(countryupper)
            if iso3 is not None:
                return iso3

        iso3 = self.countrynames2iso3.get(countryupper)
        if iso3 is not None:
            return iso3

        if exception is not None:
            raise exception
        return None

    def get_iso3_country_code_partial(self, country, exception=None):
        # type: (str, Optional[ExceptionUpperBound]) -> Tuple[Optional[str], bool]]
        """Get iso 3 code for country. A tuple is returned with the first value being the iso 3 code and the second
        showing if the match is exact or not.

        Args:
            country (str): Country for which to get iso 3 code
            exception (Optional[ExceptionUpperBound]): An exception to raise if country not found. Defaults to None.

        Returns:
            Tuple[Optional[str], bool]]: Return iso 3 code and if the match is exact or (None, False).
        """
        iso3 = self.get_iso3_country_code(country)

        if iso3 is not None:
            return iso3, True

        countryupper = country.upper()
        for countryname in self.countrynames2iso3:
            if countryupper in countryname or countryname in countryupper:
                return self.countrynames2iso3[countryname], False

        if exception is not None:
            raise exception
        return None, False

    def get_countries_in_region(self, region):
        # type: (str, Any]) -> List[str]
        """Get countries (iso 3 codes) in continent

        Args:
            region (str): Three letter region code or region name

        Returns:
            List(str): Sorted list of iso 3 country names
        """
        regionupper = region.upper()
        if regionupper in self.regionids2names:
            return self.regions2countries[regionupper]
        regionid = self.regionnames2ids.get(regionupper)
        if regionid is not None:
            return self.regions2countries[regionid]
        return list()
