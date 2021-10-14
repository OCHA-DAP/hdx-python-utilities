"""Saver Tests"""
import json
from collections import OrderedDict
from os.path import join

import pytest

from hdx.utilities.compare import assert_files_same
from hdx.utilities.saver import save_json, save_yaml


class TestLoader:
    yaml_to_write = OrderedDict(
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

    json_to_write = OrderedDict(
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

    @pytest.fixture(scope="session")
    def saverfolder(self, fixturesfolder):
        return join(fixturesfolder, "saver")

    @pytest.mark.parametrize(
        "filename,pretty,sortkeys",
        [
            ("pretty-false_sortkeys-false.yaml", False, False),
            ("pretty-false_sortkeys-true.yaml", False, True),
            ("pretty-true_sortkeys-false.yaml", True, False),
            ("pretty-true_sortkeys-true.yaml", True, True),
        ],
    )
    def test_save_yaml(self, tmpdir, saverfolder, filename, pretty, sortkeys):
        test_path = join(str(tmpdir), filename)
        ref_path = join(saverfolder, filename)
        save_yaml(
            TestLoader.yaml_to_write,
            test_path,
            pretty=pretty,
            sortkeys=sortkeys,
        )
        assert_files_same(ref_path, test_path)
        dct = json.loads(json.dumps(TestLoader.yaml_to_write))
        save_yaml(dct, test_path, pretty=pretty, sortkeys=sortkeys)
        assert_files_same(ref_path, test_path)

    @pytest.mark.parametrize(
        "filename,pretty,sortkeys",
        [
            ("pretty-false_sortkeys-false.json", False, False),
            ("pretty-false_sortkeys-true.json", False, True),
            ("pretty-true_sortkeys-false.json", True, False),
            ("pretty-true_sortkeys-true.json", True, True),
        ],
    )
    def test_save_json(self, tmpdir, saverfolder, filename, pretty, sortkeys):
        test_path = join(str(tmpdir), filename)
        ref_path = join(saverfolder, filename)
        save_json(
            TestLoader.json_to_write,
            test_path,
            pretty=pretty,
            sortkeys=sortkeys,
        )
        assert_files_same(ref_path, test_path)
        dct = json.loads(json.dumps(TestLoader.json_to_write))
        save_json(dct, test_path, pretty=pretty, sortkeys=sortkeys)
        assert_files_same(ref_path, test_path)
