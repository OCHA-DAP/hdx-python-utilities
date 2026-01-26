from collections import OrderedDict

from hdx.utilities.url import (
    get_filename_extension_from_url,
    get_filename_from_url,
    get_url_for_get,
    get_url_params_for_post,
)


class TestURL:
    def test_get_filename_extension_from_url(self, fixtureurl):
        filename = get_filename_from_url("http://test.com/test.csv", second_last=True)
        assert filename == "test.csv"
        filename = get_filename_from_url("http://test.com/test/test.csv", True)
        assert filename == "test_test.csv"
        filename = get_filename_from_url(
            "https://globalhealth5050.org/?_covid-data=dataset-fullvars&_extype=csv",
            second_last=True,
        )
        assert filename == "covid-data-dataset-fullvars-extype-csv"
        filename = get_filename_from_url(fixtureurl)
        assert filename == "test_data.csv"
        filename = get_filename_from_url(fixtureurl, second_last=True)
        assert filename == "fixtures_test_data.csv"
        filename, extension = get_filename_extension_from_url(fixtureurl)
        assert filename == "test_data"
        assert extension == ".csv"
        filename, extension = get_filename_extension_from_url(
            fixtureurl, second_last=True
        )
        assert filename == "fixtures_test_data"
        assert extension == ".csv"

    def test_get_url_for_get(self):
        assert (
            get_url_for_get(
                "http://www.lala.com/hdfa?a=3&b=4",
                OrderedDict([("c", "e"), ("d", "f")]),
            )
            == "http://www.lala.com/hdfa?a=3&b=4&c=e&d=f"
        )
        assert (
            get_url_for_get("http://www.lala.com/hdfa?a=3&b=4", {"c": "e", "d": "f"})
            == "http://www.lala.com/hdfa?a=3&b=4&c=e&d=f"
        )

    def test_get_url_params_for_post(self):
        result = get_url_params_for_post(
            "http://www.lala.com/hdfa?a=3&b=4",
            OrderedDict([("c", "e"), ("d", "f")]),
        )
        assert result[0] == "http://www.lala.com/hdfa"
        assert list(result[1].items()) == list(
            OrderedDict([("a", "3"), ("b", "4"), ("c", "e"), ("d", "f")]).items()
        )
        result = get_url_params_for_post(
            "http://www.lala.com/hdfa?a=3&b=4", {"c": "e", "d": "f"}
        )
        assert result[0] == "http://www.lala.com/hdfa"
        assert list(result[1].items()) == list(
            OrderedDict([("a", "3"), ("b", "4"), ("c", "e"), ("d", "f")]).items()
        )
