# -*- coding: UTF-8 -*-
"""location Tests"""
import pytest

from hdx.utilities.loader import load_json
from hdx.utilities.location import Location
from hdx.utilities.path import script_dir_plus_file


class LocationError(Exception):
    pass

class TestLocation:
    @pytest.fixture(scope='class')
    def location(self):
        return Location.set_data_url(None)

    def test_get_country_name_from_iso3(self, location):
        assert Location.get_country_name_from_iso3('jpn') == 'Japan'
        assert Location.get_country_name_from_iso3('awe') is None
        assert Location.get_country_name_from_iso3('Pol') == 'Poland'
        assert Location.get_country_name_from_iso3('SGP') == 'Singapore'
        assert Location.get_country_name_from_iso3('uy') is None
        with pytest.raises(LocationError):
            Location.get_country_name_from_iso3('uy', exception=LocationError)
        assert Location.get_country_name_from_iso3('uy') is None
        assert Location.get_country_name_from_iso3('VeN') == 'Venezuela, RB'

    def test_get_country_info_from_iso2(self, location):
        assert Location.get_country_info_from_iso2('jp') == {'name': 'Japan', 'lendingType': {'value': 'Not classified', 'id': 'LNX'}, 'latitude': '35.67', 'incomeLevel': {'value': 'High income', 'id': 'HIC'}, 'id': 'JPN', 'iso2Code': 'JP', 'longitude': '139.77', 'region': {'value': 'East Asia & Pacific', 'id': 'EAS'}, 'adminregion': {'value': '', 'id': ''}, 'capitalCity': 'Tokyo'}
        assert Location.get_country_info_from_iso2('ab') is None
        with pytest.raises(LocationError):
            Location.get_country_info_from_iso2('ab', exception=LocationError)

    def test_get_country_name_from_iso2(self, location):
        assert Location.get_country_name_from_iso2('jp') == 'Japan'
        assert Location.get_country_name_from_iso2('ab') is None
        assert Location.get_country_name_from_iso2('Pl') == 'Poland'
        assert Location.get_country_name_from_iso2('SG') == 'Singapore'
        assert Location.get_country_name_from_iso2('SGP') is None
        with pytest.raises(LocationError):
            Location.get_country_name_from_iso2('SGP', exception=LocationError)
        assert Location.get_country_name_from_iso2('VE') == 'Venezuela, RB'

    def test_get_iso3_country_code(self, location):
        assert Location.get_iso3_country_code('jpn') == 'JPN'
        assert Location.get_iso3_country_code('jp') == 'JPN'
        assert Location.get_iso3_country_code_partial('jpn') == ('JPN', True)
        assert Location.get_iso3_country_code_partial('ZWE') == ('ZWE', True)
        assert Location.get_iso3_country_code_partial('Vut') == ('VUT', True)
        assert Location.get_iso3_country_code('abc') is None
        with pytest.raises(LocationError):
            Location.get_iso3_country_code('abc', exception=LocationError)
        assert Location.get_iso3_country_code_partial('abc') == (None, False)
        with pytest.raises(LocationError):
            Location.get_iso3_country_code_partial('abc', exception=LocationError)
        assert Location.get_iso3_country_code_partial('United Kingdom') == ('GBR', True)
        assert Location.get_iso3_country_code_partial('united states') == ('USA', True)
        assert Location.get_iso3_country_code('UZBEKISTAN') == 'UZB'
        assert Location.get_iso3_country_code_partial('UZBEKISTAN') == ('UZB', True)
        assert Location.get_iso3_country_code('Sierra') is None
        assert Location.get_iso3_country_code_partial('Sierra') == ('SLE', False)
        assert Location.get_iso3_country_code('Venezuela') is None
        assert Location.get_iso3_country_code_partial('Venezuela') == ('VEN', False)
        with pytest.raises(ValueError):
            Location.get_iso3_country_code('abc', exception=ValueError)
        with pytest.raises(ValueError):
            Location.get_iso3_country_code_partial('abc', exception=ValueError)


    def test_get_countries_in_region(self, location):
        assert len(Location.get_countries_in_region('SSF')) == 48
        assert Location.get_countries_in_region('South Asia') == ['AFG', 'BGD', 'BTN', 'IND', 'LKA',
                                                                  'MDV', 'NPL', 'PAK']
        assert len(Location.get_countries_in_region('NOTEXIST')) == 0
        with pytest.raises(LocationError):
            Location.get_countries_in_region('NOTEXIST', exception=LocationError)

    def test_wb_feed_file_working(self):
        Location.set_data_url(Location._wburl)
        Location._countriesdata = None
        assert len(Location.get_countries_in_region('SSF')) == 48
        json = load_json(script_dir_plus_file('countries.json', TestLocation))
        data = json[1]
        Location.set_countriesdata(data)
        assert Location.get_iso3_country_code('UZBEKISTAN') is None
        Location.set_data_url('NOTEXIST')
        Location._countriesdata = None
        assert Location.get_iso3_country_code('UZBEKISTAN') == 'UZB'
