# -*- coding: UTF-8 -*-
"""Loader Tests"""
from os.path import join

import pytest

from hdx.utilities.loader import load_yaml, load_json, load_and_merge_yaml, load_and_merge_json, LoadError, \
    load_file_to_str, load_yaml_into_existing_dict, load_json_into_existing_dict


class TestLoader:
    expected_yaml = {
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

    expected_json = {
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

    def test_load_empty(self, fixturesfolder):
        loaderfolder = join(fixturesfolder, 'loader')
        with pytest.raises(LoadError):
            load_file_to_str(join(loaderfolder, 'empty.yml'))
        with pytest.raises(LoadError):
            load_yaml(join(loaderfolder, 'empty.yml'))
        with pytest.raises(LoadError):
            load_json(join(loaderfolder, 'empty.json'))

    def test_load_and_merge_yaml(self, configfolder):
        result = load_and_merge_yaml([join(configfolder, 'hdx_config.yml'),
                                      join(configfolder, 'project_configuration.yml')])
        assert result == TestLoader.expected_yaml

    def test_load_and_merge_json(self, configfolder):
        result = load_and_merge_json([join(configfolder, 'hdx_config.json'),
                                      join(configfolder, 'project_configuration.json')])

        assert result == TestLoader.expected_json

    def test_load_yaml_into_existing_dict(self, configfolder):
        existing_dict = load_yaml(join(configfolder, 'hdx_config.yml'))
        result = load_yaml_into_existing_dict(existing_dict,
                                              join(configfolder, 'project_configuration.yml'))
        assert result == TestLoader.expected_yaml

    def test_load_json_into_existing_dict(self, configfolder):
        existing_dict = load_json(join(configfolder, 'hdx_config.json'))
        result = load_json_into_existing_dict(existing_dict,
                                              join(configfolder, 'project_configuration.json'))
        assert result == TestLoader.expected_json
