"""Saver Tests"""
import json
from collections import OrderedDict
from os.path import exists, join

import pytest

from hdx.utilities.compare import assert_files_same
from hdx.utilities.loader import load_yaml
from hdx.utilities.saver import save_hxlated_output, save_json, save_yaml


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

    @pytest.fixture(scope="class")
    def saverfolder(self, fixturesfolder):
        return join(fixturesfolder, "saver")

    @pytest.fixture(scope="class")
    def json_csv_configuration(self, fixturesfolder):
        return load_yaml(join(fixturesfolder, "config", "json_csv.yml"))

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

    def test_save_hxlated_output(
        self, tmpdir, saverfolder, json_csv_configuration
    ):
        rows = (
            ("Col1", "Col2", "Col3"),
            ("#tag1", "#tag2", "#tag3"),
            (1, "2", 3),
            (4, "5", 6),
        )
        output_dir = str(tmpdir)

        save_hxlated_output(
            json_csv_configuration["test1"],
            rows[2:],
            includes_header=False,
            includes_hxltags=False,
            output_dir=output_dir,
        )
        filename = "out.csv"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
        filename = "out.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        row0 = rows[0]
        rowsdict = []
        for row in rows[2:]:
            newrow = {}
            for i, key in enumerate(row0):
                newrow[key] = row[i]
            rowsdict.append(newrow)
        save_hxlated_output(
            json_csv_configuration["test1"],
            rowsdict,
            includes_header=False,
            includes_hxltags=False,
            output_dir=output_dir,
        )
        filename = "out.csv"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
        filename = "out.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test2"],
            rows,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out2.csv"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
        filename = "out2.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        rowsdict = []
        for row in rows[1:]:
            newrow = {}
            for i, key in enumerate(row0):
                newrow[key] = row[i]
            rowsdict.append(newrow)
        save_hxlated_output(
            json_csv_configuration["test2"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out2.csv"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
        filename = "out2.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test3"],
            rows,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out3.csv"
        assert_files_same(
            join(saverfolder, "out.csv"), join(output_dir, filename)
        )
        filename = "out3.json"
        assert exists(join(output_dir, filename)) is False

        save_hxlated_output(
            json_csv_configuration["test4"],
            rows,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out4.csv"
        assert exists(join(output_dir, filename)) is False
        filename = "out4.json"
        assert_files_same(
            join(saverfolder, "out2.json"), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test5"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out5.csv"
        assert_files_same(
            join(saverfolder, "out2.csv"), join(output_dir, filename)
        )
        filename = "out5.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test6"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out6.csv"
        assert_files_same(
            join(saverfolder, "out2.csv"), join(output_dir, filename)
        )
        filename = "out6.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test7"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out7.csv"
        assert_files_same(
            join(saverfolder, "out2.csv"), join(output_dir, filename)
        )
        filename = "out7.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )

        save_hxlated_output(
            json_csv_configuration["test8"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out8.csv"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
        filename = "out8.json"
        assert_files_same(
            join(saverfolder, filename), join(output_dir, filename)
        )
