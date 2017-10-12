# -*- coding: UTF-8 -*-
"""location Tests"""
import pytest

from hdx.utilities.location import Location

class LocationError(Exception):
    pass

class TestLocation:
    @pytest.fixture(scope='class')
    def location(self):
        return Location(url='NOTEXIST')

    def test_get_country_name_from_iso3(self, location):
        assert location.get_country_name_from_iso3('jpn') == 'Japan'
        assert location.get_country_name_from_iso3('awe') is None
        assert location.get_country_name_from_iso3('Pol') == 'Poland'
        assert location.get_country_name_from_iso3('SGP') == 'Singapore'
        assert location.get_country_name_from_iso3('uy') is None
        with pytest.raises(LocationError):
            location.get_country_name_from_iso3('uy', exception=LocationError)
        assert location.get_country_name_from_iso3('uy') is None
        assert location.get_country_name_from_iso3('VeN') == 'Venezuela, RB'

    def test_get_country_info_from_iso2(self, location):
        assert location.get_country_info_from_iso2('jp') == {'name': 'Japan', 'lendingType': {'value': 'Not classified', 'id': 'LNX'}, 'latitude': '35.67', 'incomeLevel': {'value': 'High income', 'id': 'HIC'}, 'id': 'JPN', 'iso2Code': 'JP', 'longitude': '139.77', 'region': {'value': 'East Asia & Pacific', 'id': 'EAS'}, 'adminregion': {'value': '', 'id': ''}, 'capitalCity': 'Tokyo'}
        assert location.get_country_info_from_iso2('ab') is None
        with pytest.raises(LocationError):
            location.get_country_info_from_iso2('ab', exception=LocationError)

    def test_get_country_name_from_iso2(self, location):
        assert location.get_country_name_from_iso2('jp') == 'Japan'
        assert location.get_country_name_from_iso2('ab') is None
        assert location.get_country_name_from_iso2('Pl') == 'Poland'
        assert location.get_country_name_from_iso2('SG') == 'Singapore'
        assert location.get_country_name_from_iso2('SGP') is None
        with pytest.raises(LocationError):
            location.get_country_name_from_iso2('SGP', exception=LocationError)
        assert location.get_country_name_from_iso2('VE') == 'Venezuela, RB'

    def test_get_iso3_country_code(self, location):
        assert location.get_iso3_country_code('jpn') == 'JPN'
        assert location.get_iso3_country_code('jp') == 'JPN'
        assert location.get_iso3_country_code_partial('jpn') == ('JPN', True)
        assert location.get_iso3_country_code_partial('ZWE') == ('ZWE', True)
        assert location.get_iso3_country_code_partial('Vut') == ('VUT', True)
        assert location.get_iso3_country_code('abc') is None
        with pytest.raises(LocationError):
            location.get_iso3_country_code('abc', exception=LocationError)
        assert location.get_iso3_country_code_partial('abc') == (None, False)
        assert location.get_iso3_country_code_partial('United Kingdom') == ('GBR', True)
        assert location.get_iso3_country_code_partial('united states') == ('USA', True)
        assert location.get_iso3_country_code('UZBEKISTAN') == 'UZB'
        assert location.get_iso3_country_code_partial('UZBEKISTAN') == ('UZB', True)
        assert location.get_iso3_country_code('Sierra') is None
        assert location.get_iso3_country_code_partial('Sierra') == ('SLE', False)
        assert location.get_iso3_country_code('Venezuela') is None
        assert location.get_iso3_country_code_partial('Venezuela') == ('VEN', False)
        with pytest.raises(ValueError):
            location.get_iso3_country_code('abc', exception=ValueError)
        with pytest.raises(ValueError):
            location.get_iso3_country_code_partial('abc', exception=ValueError)

    def test_get_countries_in_region(self, location):
        assert len(location.get_countries_in_region('SSF')) == 48
        assert location.get_countries_in_region('South Asia') == ['AFG', 'BGD', 'BTN', 'IND', 'LKA',
                                                                  'MDV', 'NPL', 'PAK']
        assert len(location.get_countries_in_region('NOTEXIST')) == 0

    def test_wb_feed_working(self):
        assert len(Location().get_countries_in_region('SSF')) == 48
