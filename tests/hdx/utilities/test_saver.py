"""Saver Tests"""

import json
from collections import OrderedDict
from copy import deepcopy
from os import remove
from os.path import exists, join

import pytest

from hdx.utilities.compare import assert_files_same
from hdx.utilities.dictandlist import read_list_from_csv
from hdx.utilities.loader import load_yaml
from hdx.utilities.path import temp_dir
from hdx.utilities.saver import save_hxlated_output, save_iterable, save_json, save_yaml


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
                OrderedDict([("required_fields", ["name", "title", "dataset_date"])]),
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
        return load_yaml(join(fixturesfolder, "config", "json_csv.yaml"))

    @pytest.mark.parametrize(
        "filename,pretty,sortkeys",
        [
            ("pretty-false_sortkeys-false.yaml", False, False),
            ("pretty-false_sortkeys-true.yaml", False, True),
            ("pretty-true_sortkeys-false.yaml", True, False),
            ("pretty-true_sortkeys-true.yaml", True, True),
        ],
    )
    def test_save_yaml(self, tmp_path, saverfolder, filename, pretty, sortkeys):
        test_path = join(str(tmp_path), filename)
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
    def test_save_json(self, tmp_path, saverfolder, filename, pretty, sortkeys):
        test_path = join(str(tmp_path), filename)
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

    def test_save_hxlated_output(self, tmp_path, saverfolder, json_csv_configuration):
        rows = (
            ("Col1", "Col2", "Col3"),
            ("#tag1", "#tag2", "#tag3"),
            (1, "2", 3),
            (4, "5", 6),
        )
        output_dir = str(tmp_path)

        save_hxlated_output(
            json_csv_configuration["test1"],
            rows[2:],
            includes_header=False,
            includes_hxltags=False,
            output_dir=output_dir,
        )
        filename = "out.csv"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))
        filename = "out.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

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
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))
        filename = "out.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test2"],
            rows,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out2.csv"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))
        filename = "out2.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

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
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))
        filename = "out2.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test3"],
            rows,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out3.csv"
        assert_files_same(join(saverfolder, "out.csv"), join(output_dir, filename))
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
        assert_files_same(join(saverfolder, "out2.json"), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test5"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
        )
        filename = "out5.csv"
        assert_files_same(join(saverfolder, "out2.csv"), join(output_dir, filename))
        filename = "out5.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test6"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out6.csv"
        assert_files_same(join(saverfolder, "out2.csv"), join(output_dir, filename))
        filename = "out6.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test7"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out7.csv"
        assert_files_same(join(saverfolder, "out2.csv"), join(output_dir, filename))
        filename = "out7.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

        save_hxlated_output(
            json_csv_configuration["test8"],
            rowsdict,
            includes_header=True,
            includes_hxltags=True,
            output_dir=output_dir,
            today="today!",
        )
        filename = "out8.csv"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))
        filename = "out8.json"
        assert_files_same(join(saverfolder, filename), join(output_dir, filename))

    def test_save_iterable(self):
        list_of_tuples = [(1, 2, 3, "a"), (4, 5, 6, "b"), (7, 8, 9, "c")]
        list_of_lists = [[1, 2, 3, "a"], [4, 5, 6, "b"], [7, 8, 9, "c"]]
        list_of_dicts = [
            {"h1": "1", "h2": "2", "h4": "a", "h3": "3"},
            {"h1": "4", "h2": "5", "h4": "b", "h3": "6"},
            {"h1": "7", "h2": "8", "h4": "c", "h3": "9"},
        ]

        with temp_dir(
            "TestSaveIterable",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            filename = "test_save_iterable_to_csv.csv"
            filepath = join(tempdir, filename)
            rows = save_iterable(
                filepath, list_of_lists, headers=["h1", "h2", "h3", "h4"]
            )
            assert rows == list_of_lists
            newll = read_list_from_csv(filepath)
            newld = read_list_from_csv(filepath, headers=1, dict_form=True)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            assert newld == [
                {"h1": "1", "h2": "2", "h4": "a", "h3": "3"},
                {"h1": "4", "h2": "5", "h4": "b", "h3": "6"},
                {"h1": "7", "h2": "8", "h4": "c", "h3": "9"},
            ]

            rows = save_iterable(
                filepath, list_of_dicts, columns=["h3", "h2", "h1", "h4"]
            )
            assert rows == list_of_dicts
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h3", "h2", "h1", "h4"],
                ["3", "2", "1", "a"],
                ["6", "5", "4", "b"],
                ["9", "8", "7", "c"],
            ]

            save_iterable(filepath, list_of_dicts, columns=["h2", "h3", "h1"])
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h2", "h3", "h1"],
                ["2", "3", "1"],
                ["5", "6", "4"],
                ["8", "9", "7"],
            ]

            xlfilepath = filepath.replace("csv", "xlsx")
            rows = save_iterable(
                xlfilepath,
                list_of_lists,
                headers=["h1", "h2", "h3", "h4"],
                format="xlsx",
            )
            assert rows == list_of_lists
            assert exists(xlfilepath), "File should exist"

            save_iterable(filepath, list_of_tuples, headers=("h1", "h2", "h3", "h4"))
            newll = read_list_from_csv(filepath)
            newld = read_list_from_csv(filepath, headers=1, dict_form=True)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            assert newld == [
                {"h1": "1", "h2": "2", "h4": "a", "h3": "3"},
                {"h1": "4", "h2": "5", "h4": "b", "h3": "6"},
                {"h1": "7", "h2": "8", "h4": "c", "h3": "9"},
            ]
            save_iterable(filepath, list_of_lists, headers=["h1", "h2", "h3"])
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3"],
                ["1", "2", "3"],
                ["4", "5", "6"],
                ["7", "8", "9"],
            ]
            save_iterable(
                filepath,
                list_of_lists,
                headers=["h1", "h3", "h4"],
                columns=[1, 3, 4],
            )
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h3", "h4"],
                ["1", "3", "a"],
                ["4", "6", "b"],
                ["7", "9", "c"],
            ]

            def row_func(row):
                row[1] = row[1] + 1
                return row

            list_of_lists_copy = deepcopy(list_of_lists)
            rows = save_iterable(
                filepath,
                list_of_lists_copy,
                headers=["h1", "h2", "h3", "h4"],
                row_function=row_func,
            )
            assert rows == [[1, 3, 3, "a"], [4, 6, 6, "b"], [7, 9, 9, "c"]]
            newll = read_list_from_csv(filepath)
            newld = read_list_from_csv(filepath, headers=1, dict_form=True)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "3", "3", "a"],
                ["4", "6", "6", "b"],
                ["7", "9", "9", "c"],
            ]
            assert newld == [
                {"h1": "1", "h2": "3", "h4": "a", "h3": "3"},
                {"h1": "4", "h2": "6", "h4": "b", "h3": "6"},
                {"h1": "7", "h2": "9", "h4": "c", "h3": "9"},
            ]

            list_of_lists = [
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                [7, 8, 9, "c"],
            ]
            save_iterable(filepath, list_of_lists)
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            save_iterable(filepath, list_of_lists, headers=2)
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]

            list_of_dicts = [
                {"h1": 1, "h2": 2, "h3": 3, "h4": "a"},
                {"h1": 4, "h2": 5, "h3": 6, "h4": "b"},
                {"h1": 7, "h2": 8, "h3": 9, "h4": "c"},
            ]
            save_iterable(filepath, list_of_dicts, headers=["h1", "h2", "h3", "h4"])
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            save_iterable(filepath, list_of_dicts)
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            save_iterable(filepath, list_of_dicts, headers=2)
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["1", "2", "3", "a"],
                ["4", "5", "6", "b"],
                ["7", "8", "9", "c"],
            ]
            save_iterable(
                filepath,
                list_of_dicts,
                headers=["h1", "h3", "h4"],
                columns=["h1", "h3", "h4"],
            )
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h3", "h4"],
                ["1", "3", "a"],
                ["4", "6", "b"],
                ["7", "9", "c"],
            ]

            def row_func(row):
                row["h3"] = row["h3"] + 1
                return row

            save_iterable(
                filepath,
                list_of_dicts,
                headers=["h1", "h2", "h3", "h4"],
                row_function=row_func,
            )
            newll = read_list_from_csv(filepath)
            remove(filepath)
            assert newll == [
                ["h1", "h2", "h3", "h4"],
                ["1", "2", "4", "a"],
                ["4", "5", "7", "b"],
                ["7", "8", "10", "c"],
            ]

            with pytest.raises(ValueError):
                read_list_from_csv(filepath, dict_form=True)

            rows = save_iterable(filepath, [], headers=["h1", "h3", "h4"])
            assert rows == []
