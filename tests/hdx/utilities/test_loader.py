# -*- coding: UTF-8 -*-
"""Loader Tests"""
from os.path import join

import pytest

from hdx.utilities.loader import load_yaml, load_json, load_and_merge_yaml, load_and_merge_json, LoadError


class TestLoader:
    def test_load_empty(self, fixturesfolder):
        loaderfolder = join(fixturesfolder, 'loader')
        with pytest.raises(LoadError):
            load_yaml(join(loaderfolder, 'empty.yml'))
        with pytest.raises(LoadError):
            load_json(join(loaderfolder, 'empty.json'))

    def test_load_and_merge_yaml(self, configfolder):
        result = load_and_merge_yaml([join(configfolder, 'hdx_config.yml'),
                                      join(configfolder, 'project_configuration.yml')])
        expected = {
            'param_1': 'ABC',
            'hdx_prod_site': {
                'url': 'https://data.humdata.org/',
                'username': None,
                'password': None
            },
            'hdx_test_site': {
                'url': 'https://test-data.humdata.org/',
                'username': 'lala',
                'password': 'lalala'
            },
            'dataset': {'required_fields': [
                'name',
                'title',
                'dataset_date',
            ]},
            'resource': {'required_fields': ['package_id', 'name', 'description'
                                             ]},
            'showcase': {'required_fields': [
                'name',
                'title',
            ]},
        }

        assert result == expected

    def test_load_and_merge_json(self, configfolder):
        result = load_and_merge_json([join(configfolder, 'hdx_config.json'),
                                      join(configfolder, 'project_configuration.json')])
        expected = {
            'my_param': 'abc',
            'hdx_prod_site': {
                'url': 'https://data.humdata.org/',
                'username': None,
                'password': None
            },
            'hdx_test_site': {
                'url': 'https://test-data.humdata.org/',
                'username': 'tumteetum',
                'password': 'tumteetumteetum'
            },
            'dataset': {'required_fields': [
                'name',
                'dataset_date',
            ]},
            'resource': {'required_fields': ['name', 'description'
                                             ]},
            'showcase': {'required_fields': [
                'name',
            ], },
        }

        assert result == expected
