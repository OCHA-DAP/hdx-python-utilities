"""Loader Tests"""
from collections import OrderedDict
from os.path import join

import pytest

from hdx.utilities.loader import (
    LoadError,
    load_and_merge_json,
    load_and_merge_yaml,
    load_json,
    load_json_into_existing_dict,
    load_text,
    load_yaml,
    load_yaml_into_existing_dict,
)
from hdx.utilities.path import temp_dir
from hdx.utilities.saver import save_text


class TestLoader:
    expected_yaml = OrderedDict(
        [
            (
                "hdx_prod_site",
                OrderedDict(
                    [
                        ("url", "https://data.humdata.org/"),
                        ("username", None),
                        ("password", None),
                    ]
                ),
            ),
            (
                "hdx_test_site",
                OrderedDict(
                    [
                        ("url", "https://test-data.humdata.org/"),
                        ("username", "lala"),
                        ("password", "lalala"),
                    ]
                ),
            ),
            (
                "dataset",
                OrderedDict(
                    [("required_fields", ["name", "title", "dataset_date"])]
                ),
            ),
            (
                "resource",
                OrderedDict(
                    [
                        (
                            "required_fields",
                            ["package_id", "name", "description"],
                        )
                    ]
                ),
            ),
            (
                "showcase",
                OrderedDict([("required_fields", ["name", "title"])]),
            ),
            ("param_1", "ABC"),
        ]
    )

    expected_json = OrderedDict(
        [
            (
                "hdx_prod_site",
                OrderedDict(
                    [
                        ("url", "https://data.humdata.org/"),
                        ("username", None),
                        ("password", None),
                    ]
                ),
            ),
            (
                "hdx_test_site",
                OrderedDict(
                    [
                        ("url", "https://test-data.humdata.org/"),
                        ("username", "tumteetum"),
                        ("password", "tumteetumteetum"),
                    ]
                ),
            ),
            (
                "dataset",
                OrderedDict([("required_fields", ["name", "dataset_date"])]),
            ),
            (
                "resource",
                OrderedDict([("required_fields", ["name", "description"])]),
            ),
            ("showcase", OrderedDict([("required_fields", ["name"])])),
            ("my_param", "abc"),
        ]
    )
    text = """  hello
this
is
a
test  

"""  # noqa: W291
    expected_text_strip = """hello
this
is
a
test"""
    expected_text_newlines_to_spaces = """  hello this is a test    """

    def test_load_empty(self, fixturesfolder):
        loaderfolder = join(fixturesfolder, "loader")
        with pytest.raises(LoadError):
            load_text(join(loaderfolder, "empty.yml"))
        with pytest.raises(LoadError):
            load_yaml(join(loaderfolder, "empty.yml"))
        with pytest.raises(LoadError):
            load_json(join(loaderfolder, "empty.json"))

    def test_load_and_merge_yaml(self, configfolder):
        result = load_and_merge_yaml(
            [
                join(configfolder, "hdx_config.yml"),
                join(configfolder, "project_configuration.yml"),
            ]
        )
        assert list(result.items()) == list(TestLoader.expected_yaml.items())

    def test_load_and_merge_json(self, configfolder):
        result = load_and_merge_json(
            [
                join(configfolder, "hdx_config.json"),
                join(configfolder, "project_configuration.json"),
            ]
        )
        assert list(result.items()) == list(TestLoader.expected_json.items())

    def test_load_yaml_into_existing_dict(self, configfolder):
        existing_dict = load_yaml(join(configfolder, "hdx_config.yml"))
        result = load_yaml_into_existing_dict(
            existing_dict, join(configfolder, "project_configuration.yml")
        )
        assert list(result.items()) == list(TestLoader.expected_yaml.items())

    def test_load_json_into_existing_dict(self, configfolder):
        existing_dict = load_json(join(configfolder, "hdx_config.json"))
        result = load_json_into_existing_dict(
            existing_dict, join(configfolder, "project_configuration.json")
        )
        assert list(result.items()) == list(TestLoader.expected_json.items())

    def test_load_file_to_str(self):
        with temp_dir(folder="test_text") as tmpdir:
            text_file = join(tmpdir, "text_file.txt")
            save_text(TestLoader.text, text_file)
            result = load_text(text_file)
            assert result == TestLoader.text
            result = load_text(text_file, strip=True)
            assert result == TestLoader.expected_text_strip
            result = load_text(text_file, replace_newlines=" ")
            assert result == TestLoader.expected_text_newlines_to_spaces
            with pytest.raises(IOError):
                load_text(join(tmpdir, "NOTEXIST.txt"))
