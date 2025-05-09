"""Downloader Tests"""

import copy
import re
from collections import OrderedDict
from contextlib import contextmanager
from os import remove
from os.path import abspath, join
from shutil import copytree, rmtree
from tempfile import gettempdir

import pytest
from utils import assert_downloaders

from hdx.utilities.base_downloader import DownloadError
from hdx.utilities.downloader import Download
from hdx.utilities.session import SessionError
from hdx.utilities.useragent import UserAgent


@contextmanager
def not_raises(ExpectedException):
    try:
        yield
    except ExpectedException as error:
        raise pytest.fail(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise pytest.fail(f"An unexpected exception {error} raised.")


class TestDownloader:
    downloaderfoldername = "downloader"

    @pytest.fixture(scope="class", autouse=True)
    def useragent(self):
        UserAgent.set_global("test")
        yield
        UserAgent.clear_global()

    @pytest.fixture(scope="class")
    def downloaderfolder(self, fixturesfolder):
        return join(fixturesfolder, self.downloaderfoldername)

    @pytest.fixture(scope="class")
    def fixturefile(self, downloaderfolder):
        return join(downloaderfolder, "extra_params_tree.yaml")

    @pytest.fixture(scope="class")
    def fixtureurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/test_data.csv"

    @pytest.fixture(scope="class")
    def fixtureurlexcel(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_data.xlsx"

    @pytest.fixture(scope="class")
    def getfixtureurl(self):
        return "https://httpbin.org/get"

    @pytest.fixture(scope="class")
    def postfixtureurl(self):
        return "https://httpbin.org/post"

    @pytest.fixture(scope="class")
    def fixturenotexistsurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/NOTEXIST.csv"

    @pytest.fixture(scope="class")
    def fixtureprocessurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_csv_processing.csv?a=1"

    @pytest.fixture(scope="class")
    def fixtureprocessurlblank(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_csv_processing_blanks.csv?a=1"

    @pytest.fixture(scope="class")
    def fixturexlsurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_xls_processing.xls?a=1"

    @pytest.fixture(scope="class")
    def fixturexlsxurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_xlsx_processing.xlsx?a=1"

    @pytest.fixture(scope="class")
    def fixturejsonurl(self):
        return "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/main/tests/fixtures/downloader/test_json_processing.json?a=1"

    def test_get_path_for_url(self, tmpdir, fixtureurl, configfolder, downloaderfolder):
        tmpdir = str(tmpdir)
        filename = "test_data.csv"
        path = Download.get_path_for_url(fixtureurl, configfolder)
        assert abspath(path) == abspath(join(configfolder, filename))
        path = Download.get_path_for_url(fixtureurl, downloaderfolder)
        assert abspath(path) == abspath(join(downloaderfolder, "test_data3.csv"))
        testfolder = join(tmpdir, self.downloaderfoldername)
        rmtree(testfolder, ignore_errors=True)
        copytree(downloaderfolder, testfolder)
        path = Download.get_path_for_url(fixtureurl, testfolder, overwrite=True)
        assert abspath(path) == abspath(join(testfolder, filename))
        rmtree(testfolder)
        filename = "myfilename.txt"
        path = Download.get_path_for_url(fixtureurl, filename=filename)
        assert abspath(path) == abspath(join(gettempdir(), filename))
        path = Download.get_path_for_url(fixtureurl, downloaderfolder, filename)
        assert abspath(path) == abspath(join(downloaderfolder, filename))

    def test_init(self, monkeypatch, downloaderfolder):
        with Download(auth=("u", "p")) as downloader:
            assert downloader.session.auth == ("u", "p")
        basicauth = "Basic dXNlcjpwYXNz"
        with Download(basic_auth=basicauth) as downloader:
            assert downloader.session.auth == ("user", "pass")
        basicauthfile = join(downloaderfolder, "basicauth.txt")
        with Download(basic_auth_file=basicauthfile) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
        bearertoken = "ABCDE"
        with Download(bearer_token=bearertoken) as downloader:
            assert downloader.session.headers["Accept"] == "application/json"
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )
        bearertokenfile = join(downloaderfolder, "bearertoken.txt")
        bearertoken = "12345"
        with Download(bearer_token_file=bearertokenfile) as downloader:
            assert downloader.session.headers["Accept"] == "application/json"
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )
        extraparamsyamltree = join(downloaderfolder, "extra_params_tree.yaml")
        with Download(
            extra_params_yaml=extraparamsyamltree, extra_params_lookup="mykey"
        ) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
        monkeypatch.setenv("BASIC_AUTH", basicauth)
        with Download() as downloader:
            assert downloader.session.auth == ("user", "pass")
        bearertoken = "98765"
        monkeypatch.setenv("BEARER_TOKEN", bearertoken)
        with pytest.raises(SessionError):
            Download()
        with Download(use_auth="bearer_token") as downloader:
            assert downloader.session.headers["Accept"] == "application/json"
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )
        with Download(use_auth="basic_auth") as downloader:
            assert downloader.session.auth == ("user", "pass")
        monkeypatch.delenv("BASIC_AUTH")
        with Download() as downloader:
            assert downloader.session.headers["Accept"] == "application/json"
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )
        monkeypatch.delenv("BEARER_TOKEN")
        monkeypatch.setenv("BASIC_AUTH", basicauth)
        with pytest.raises(SessionError):
            Download(basic_auth="12345")
        with pytest.raises(SessionError):
            Download(
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="mykey",
            )
        monkeypatch.delenv("BASIC_AUTH")
        with pytest.raises(SessionError):
            Download(
                basic_auth=basicauth,
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="mykey",
            )
        with pytest.raises(SessionError):
            Download(auth=("u", "p"), basic_auth="Basic xxxxxxxxxxxxxxxx")
        extraparamsjson = join(downloaderfolder, "extra_params.json")
        with pytest.raises(SessionError):
            Download(auth=("u", "p"), basic_auth_file=extraparamsjson)
        with pytest.raises(SessionError):
            Download(
                basic_auth="Basic dXNlcjpwYXNz",
                basic_auth_file=extraparamsjson,
            )
        with pytest.raises(SessionError):
            Download(
                auth=("u", "p"),
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="mykey",
            )
        with Download(
            auth=("u", "p"),
            extra_params_yaml=extraparamsyamltree,
            extra_params_lookup="mykey",
            use_auth="basic_auth",
        ) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
        with Download(
            auth=("u", "p"),
            extra_params_yaml=extraparamsyamltree,
            extra_params_lookup="mykey",
            use_auth="auth",
        ) as downloader:
            assert downloader.session.auth == ("u", "p")
        with pytest.raises(SessionError):
            Download(
                basic_auth_file=basicauthfile,
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="mykey",
            )
        with pytest.raises(SessionError):
            Download(
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="missingkey",
            )
        with pytest.raises(IOError):
            Download(basic_auth_file="NOTEXIST")
        with pytest.raises(IOError):
            Download(bearer_token_file="NOTEXIST")
        extraparamsyaml = join(downloaderfolder, "extra_params.yaml")
        test_url = "http://www.lalala.com/lala"
        with Download(
            basic_auth_file=basicauthfile, extra_params_dict={"key1": "val1"}
        ) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
            assert downloader.get_full_url(test_url) == f"{test_url}?key1=val1"
        key = "Authorization"
        value = "lala"
        with Download(headers={key: value}) as downloader:
            assert key in downloader.session.headers
            assert downloader.session.headers.get(key) == value
        with Download(extra_params_json=extraparamsjson) as downloader:
            full_url = downloader.get_full_url(test_url)
            assert "param_1=value+1" in full_url
            assert "param_2=value_2" in full_url
            assert "param_3=12" in full_url
        with Download(extra_params_yaml=extraparamsyaml) as downloader:
            full_url = downloader.get_full_url(test_url)
            assert "param1=value1" in full_url
            assert "param2=value+2" in full_url
            assert "param3=10" in full_url
        with Download(
            extra_params_yaml=extraparamsyamltree, extra_params_lookup="mykey"
        ) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
            full_url = downloader.get_full_url(test_url)
            assert "param1=value+1" in full_url
            assert "param2=value2" in full_url
            assert "param3=11" in full_url
            assert "basic_auth" not in full_url
        monkeypatch.setenv("EXTRA_PARAMS", "param1=value2+3==,param2=value3+7")
        with Download(
            extra_params_yaml=extraparamsyamltree, extra_params_lookup="mykey"
        ) as downloader:
            assert downloader.session.auth is None
            full_url = downloader.get_full_url(test_url)
            assert "param1=value2%2B3%3D%3D" in full_url
            assert "param2=value3%2B7" in full_url
            assert "param3=11" not in full_url
            assert "basic_auth" not in full_url
        with Download(
            extra_params_yaml=extraparamsyamltree,
            extra_params_lookup="mykey",
            use_env=False,
        ) as downloader:
            assert downloader.session.auth == ("testuser", "testpass")
            full_url = downloader.get_full_url(test_url)
            assert "param1=value+1" in full_url
            assert "param2=value2" in full_url
            assert "param3=11" in full_url
            assert "basic_auth" not in full_url
        monkeypatch.delenv("EXTRA_PARAMS")
        bearertoken = "ZYXWV"
        with Download(extra_params_dict={"bearer_token": bearertoken}) as downloader:
            assert downloader.session.headers["Accept"] == "application/json"
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )
            bearertoken = "FGHIJ"
            downloader.set_bearer_token(bearertoken)
            assert (
                downloader.session.headers["Authorization"] == f"Bearer {bearertoken}"
            )

        with pytest.raises(SessionError):
            Download(
                extra_params_dict={"key1": "val1"},
                extra_params_json=extraparamsjson,
            )
        with pytest.raises(SessionError):
            Download(
                extra_params_dict={"key1": "val1"},
                extra_params_yaml=extraparamsyaml,
            )
        with pytest.raises(SessionError):
            Download(
                extra_params_dict={"key1": "val1"},
                extra_params_yaml=extraparamsyamltree,
                extra_params_lookup="mykey",
            )
        with pytest.raises(IOError):
            Download(extra_params_json="NOTEXIST")
        with pytest.raises(IOError):
            Download(extra_params_yaml="NOTEXIST")
        with not_raises(IOError):
            Download(extra_params_json="NOTEXIST", fail_on_missing_file=False)
            Download(extra_params_yaml="NOTEXIST", fail_on_missing_file=False)
            Download(basic_auth_file="NOTEXIST", fail_on_missing_file=False)

    def test_get_url_for_get(self):
        assert (
            Download.get_url_for_get(
                "http://www.lala.com/hdfa?a=3&b=4",
                OrderedDict([("c", "e"), ("d", "f")]),
            )
            == "http://www.lala.com/hdfa?a=3&b=4&c=e&d=f"
        )
        assert (
            Download.get_url_for_get(
                "http://www.lala.com/hdfa?a=3&b=4", {"c": "e", "d": "f"}
            )
            == "http://www.lala.com/hdfa?a=3&b=4&c=e&d=f"
        )

    def test_get_url_params_for_post(self):
        result = Download.get_url_params_for_post(
            "http://www.lala.com/hdfa?a=3&b=4",
            OrderedDict([("c", "e"), ("d", "f")]),
        )
        assert result[0] == "http://www.lala.com/hdfa"
        assert list(result[1].items()) == list(
            OrderedDict([("a", "3"), ("b", "4"), ("c", "e"), ("d", "f")]).items()
        )
        result = Download.get_url_params_for_post(
            "http://www.lala.com/hdfa?a=3&b=4", {"c": "e", "d": "f"}
        )
        assert result[0] == "http://www.lala.com/hdfa"
        assert list(result[1].items()) == list(
            OrderedDict([("a", "3"), ("b", "4"), ("c", "e"), ("d", "f")]).items()
        )

    def test_hxl_row(self):
        headers = ["a", "b", "c"]
        hxltags = {"b": "#b", "c": "#c"}
        assert Download.hxl_row(headers, hxltags) == ["", "#b", "#c"]
        assert Download.hxl_row(headers, hxltags, dict_form=True) == {
            "a": "",
            "b": "#b",
            "c": "#c",
        }
        assert Download.hxl_row(headers, dict()) == ["", "", ""]
        assert Download.hxl_row([], hxltags) == list()

    def test_setup_stream(
        self, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl
    ):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup("NOTEXIST://NOTEXIST.csv")
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup(fixturenotexistsurl)
        with Download() as downloader:
            downloader.setup(fixtureurl)
            headers = downloader.response.headers
            assert bool(re.match(r"7\d\d", headers["Content-Length"])) is True
        with Download() as downloader:
            downloader.setup(postfixtureurl, post=True)
            headers = downloader.response.headers
            assert bool(re.match(r"4\d\d", headers["Content-Length"])) is True
            downloader.setup(
                f"{getfixtureurl}?id=10&lala=a",
                post=False,
                parameters=OrderedDict([("b", "4"), ("d", "3")]),
            )
            assert list(downloader.get_json()["args"].items()) == list(
                OrderedDict(
                    [("b", "4"), ("d", "3"), ("id", "10"), ("lala", "a")]
                ).items()
            )
            downloader.setup(
                f"{postfixtureurl}?id=3&lala=b",
                post=True,
                parameters=OrderedDict([("a", "3"), ("c", "2")]),
            )
            assert list(downloader.get_json()["form"].items()) == list(
                OrderedDict(
                    [("a", "3"), ("c", "2"), ("id", "3"), ("lala", "b")]
                ).items()
            )

    def test_hash_stream(self, fixtureurl):
        with Download() as downloader:
            downloader.setup(fixtureurl)
            md5hash = downloader.hash_stream(fixtureurl)
            assert md5hash == "da52e60d7a7c541e6fa67076bfac49f8"

    def test_download_file(
        self,
        tmpdir,
        fixturefile,
        fixtureurl,
        fixturenotexistsurl,
        getfixtureurl,
        postfixtureurl,
    ):
        tmpdir = str(tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file("NOTEXIST://NOTEXIST.csv", folder=tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(fixturenotexistsurl)
        filename = "myfilename.txt"
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(
                fixturefile, folder=tmpdir, path=join(tmpdir, filename)
            )
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(
                fixturefile, filename=filename, path=join(tmpdir, filename)
            )
        with Download() as downloader:
            f = downloader.download_file(fixturefile, folder=tmpdir)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, "extra_params_tree.yaml"))
            f = downloader.download_file(fixtureurl, folder=tmpdir)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, "test_data.csv"))
            f = downloader.download_file(fixtureurl, folder=tmpdir, filename=filename)
            fpath = abspath(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file(
                fixtureurl, path=join(tmpdir, filename), overwrite=True
            )
            fpath = abspath(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file(
                fixtureurl, path=join(tmpdir, filename), overwrite=False
            )
            fpath = abspath(f)
            assert fpath == abspath(join(tmpdir, filename.replace(".txt", "1.txt")))
            f = downloader.download_file(
                fixtureurl, path=join(tmpdir, filename), keep=True
            )
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file(
                f"{getfixtureurl}?id=10&lala=a",
                post=False,
                parameters=OrderedDict([("b", "4"), ("d", "3")]),
                folder=tmpdir,
                filename=filename,
            )
            fpath = abspath(f)
            with open(fpath, encoding="utf-8") as fi:
                text = fi.read()
                assert '"id": "10"' in text
                assert '"lala": "a"' in text
                assert '"b": "4"' in text
                assert '"d": "3"' in text
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file(
                f"{postfixtureurl}?id=3&lala=b",
                post=True,
                parameters=OrderedDict([("a", "3"), ("c", "2")]),
                folder=tmpdir,
                filename=filename,
            )
            fpath = abspath(f)
            with open(fpath, encoding="utf-8") as fi:
                text = fi.read()
                assert '"id": "3"' in text
                assert '"lala": "b"' in text
                assert '"a": "3"' in text
                assert '"c": "2"' in text
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))

    def test_download(
        self,
        fixturefile,
        fixtureurl,
        fixturenotexistsurl,
        getfixtureurl,
        postfixtureurl,
    ):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download("NOTEXIST://NOTEXIST.csv")
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download(fixturenotexistsurl)
        with Download() as downloader:
            text = downloader.download_text(fixtureurl)
            assert downloader.get_status() == 200
            assert len(downloader.get_headers()) in (24, 25)
            assert (
                bool(re.match(r"7\d\d", downloader.get_header("Content-Length")))
                is True
            )
            assert (
                text
                == """GWNO,EVENT_ID_CNTY,EVENT_ID_NO_CNTY,EVENT_DATE,YEAR,TIME_PRECISION,EVENT_TYPE,ACTOR1,ALLY_ACTOR_1,INTER1,ACTOR2,ALLY_ACTOR_2,INTER2,INTERACTION,COUNTRY,ADMIN1,ADMIN2,ADMIN3,LOCATION,LATITUDE,LONGITUDE,GEO_PRECISION,SOURCE,NOTES,FATALITIES
615,1416RTA,,18/04/2001,2001,1,Violence against civilians,Police Forces of Algeria (1999-),,1,Civilians (Algeria),Berber Ethnic Group (Algeria),7,17,Algeria,Tizi Ouzou,Beni-Douala,,Beni Douala,36.61954,4.08282,1,Associated Press Online,A Berber student was shot while in police custody at a police station in Beni Douala. He later died on Apr.21.,1
615,2229RTA,,19/04/2001,2001,1,Riots/Protests,Rioters (Algeria),Berber Ethnic Group (Algeria),5,Police Forces of Algeria (1999-),,1,15,Algeria,Tizi Ouzou,Tizi Ouzou,,Tizi Ouzou,36.71183,4.04591,3,Kabylie report,"Riots were reported in numerous villages in Kabylie, resulting in dozens wounded in clashes between protesters and police and significant material damage.",0
615,2230RTA,,20/04/2001,2001,1,Riots/Protests,Protesters (Algeria),Students (Algeria),6,,,0,60,Algeria,Bejaia,Amizour,,Amizour,36.64022,4.90131,1,Crisis Group,Students protested in the Amizour area. At least 3 were later arrested for allegedly insulting gendarmes.,0
615,2231RTA,,21/04/2001,2001,1,Riots/Protests,Rioters (Algeria),Berber Ethnic Group (Algeria),5,Police Forces of Algeria (1999-),,1,15,Algeria,Bejaia,Amizour,,Amizour,36.64022,4.90131,1,Kabylie report,"Rioters threw molotov cocktails, rocks and burning tires at gendarmerie stations in Beni Douala, El-Kseur and Amizour.",0
"""
            )
            downloader.download(
                f"{getfixtureurl}?id=10&lala=a",
                post=False,
                parameters=OrderedDict([("b", "4"), ("d", "3")]),
            )
            assert list(downloader.get_json()["args"].items()) == list(
                OrderedDict(
                    [("b", "4"), ("d", "3"), ("id", "10"), ("lala", "a")]
                ).items()
            )
            json = downloader.download_json(
                f"{postfixtureurl}?id=3&lala=b",
                post=True,
                parameters=OrderedDict([("a", "3"), ("c", "2")]),
            )
            assert list(json["form"].items()) == list(
                OrderedDict(
                    [("a", "3"), ("c", "2"), ("id", "3"), ("lala", "b")]
                ).items()
            )
        with Download(rate_limit={"calls": 1, "period": 0.1}) as downloader:
            downloader.download(
                f"{getfixtureurl}?id=10&lala=a",
                post=False,
                parameters=OrderedDict([("b", "4"), ("d", "3")]),
            )
            assert list(downloader.get_json()["args"].items()) == list(
                OrderedDict(
                    [("b", "4"), ("d", "3"), ("id", "10"), ("lala", "a")]
                ).items()
            )
            yaml = downloader.download_yaml(fixturefile)
            assert list(yaml["mykey"].items()) == list(
                OrderedDict(
                    [
                        ("param1", "value 1"),
                        ("param2", "value2"),
                        ("param3", 11),
                        ("basic_auth", "Basic dGVzdHVzZXI6dGVzdHBhc3M="),
                    ]
                ).items()
            )

    def test_download_tabular_key_value(
        self, fixtureurl, fixtureurlexcel, fixtureprocessurl
    ):
        with Download() as downloader:
            result = downloader.download_tabular_key_value(
                fixtureurl,
                file_type="csv",
                delimiter=",",
                skip_initial_space=True,
                infer_types=True,
            )
            assert result == {615: "2231RTA", "GWNO": "EVENT_ID_CNTY"}
            result = downloader.download_tabular_key_value(
                fixtureurlexcel,
                file_type="xlsx",
                sheet="test_data",
                infer_types=True,
            )
            assert result == {615: "2231RTA", "GWNO": "EVENT_ID_CNTY"}
            result = downloader.download_tabular_key_value(fixtureprocessurl, headers=3)
            assert result == {"coal": "3", "gas": "2"}
            with pytest.raises(DownloadError):
                downloader.download_tabular_key_value("NOTEXIST://NOTEXIST.csv")

    def test_get_tabular_rows_as_list(self, fixtureprocessurl):
        with Download() as downloader:
            headers, rows = downloader.get_tabular_rows_as_list(fixtureprocessurl)
            rows = list(rows)
            assert rows == [
                ["la1", "ha1", "ba1", "ma1"],
                ["header1", "header2", "header3", "header4"],
                ["coal", "3", "7.4", "'needed'"],
                ["gas", "2", "6.5", "'n/a'"],
            ]

    def test_get_tabular_rows_as_dict(self, fixtureprocessurl):
        with Download() as downloader:
            headers, rows = downloader.get_tabular_rows_as_dict(fixtureprocessurl)
            rows = list(rows)
            assert rows == [
                {
                    "la1": "header1",
                    "ha1": "header2",
                    "ba1": "header3",
                    "ma1": "header4",
                },
                {"la1": "coal", "ha1": "3", "ba1": "7.4", "ma1": "'needed'"},
                {"la1": "gas", "ha1": "2", "ba1": "6.5", "ma1": "'n/a'"},
            ]

    def test_get_tabular_rows(self, fixtureprocessurl, fixtureprocessurlblank):
        with Download() as downloader:
            expected = [
                ["la1", "ha1", "ba1", "ma1"],
                ["header1", "header2", "header3", "header4"],
                ["coal", "3", "7.4", "'needed'"],
                ["gas", "2", "6.5", "'n/a'"],
            ]
            expected_headers = expected[0]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl)
            assert headers == expected_headers
            assert list(iterator) == expected[1:]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank)
            assert headers == expected_headers
            blank_expected = copy.deepcopy(expected[1:])
            blank_expected[2][0] = None
            assert list(iterator) == blank_expected
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurlblank, ignore_blank_rows=False
            )
            assert headers == expected_headers
            blank_expected.append([None, None, None, None])
            blank_expected.insert(1, [None, None, None, None])
            assert list(iterator) == blank_expected
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=1
            )
            assert headers == expected_headers
            assert list(iterator) == expected[1:]
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=2
            )
            assert headers == expected[1]
            assert list(iterator) == expected[2:]
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=[1, 2]
            )
            assert headers == [
                "la1 header1",
                "ha1 header2",
                "ba1 header3",
                "ma1 header4",
            ]
            assert list(iterator) == expected[2:]
            myheaders = ["a", "b", "c", "d"]
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=myheaders
            )
            assert headers == myheaders
            assert list(iterator) == expected
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=1, dict_form=True
            )
            assert headers == expected_headers
            expected_dicts = [
                {
                    "la1": "header1",
                    "ha1": "header2",
                    "ba1": "header3",
                    "ma1": "header4",
                },
                {"la1": "coal", "ha1": "3", "ba1": "7.4", "ma1": "'needed'"},
                {"la1": "gas", "ha1": "2", "ba1": "6.5", "ma1": "'n/a'"},
            ]
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl, headers=3, dict_form=True
            )
            assert headers == expected[2]
            expected_dicts = [
                {"coal": "gas", "3": "2", "7.4": "6.5", "'needed'": "'n/a'"}
            ]
            assert list(iterator) == expected_dicts

            def testfn(headers, row):
                row.insert(2, "lala")
                return row

            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl,
                headers=3,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            expected_headers = ["coal", "3", "la", "7.4", "'needed'"]
            assert headers == expected_headers
            assert list(iterator) == [["gas", "2", "lala", "6.5", "'n/a'"]]

            def testfn(headers, row):
                row["la"] = "lala"
                return row

            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurl,
                headers=3,
                dict_form=True,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            assert headers == expected_headers
            expected_dicts[0]["la"] = "lala"
            assert list(iterator) == expected_dicts

            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurlblank,
                headers=1,
                dict_form=True,
                ignore_blank_rows=False,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            expected_headers = ["la1", "ha1", "la", "ba1", "ma1"]
            assert headers == expected_headers

            expected_dicts = [
                {
                    "la1": "header1",
                    "ha1": "header2",
                    "ba1": "header3",
                    "ma1": "header4",
                    "la": "lala",
                },
                {
                    "la1": None,
                    "ha1": None,
                    "ba1": None,
                    "ma1": None,
                    "la": "lala",
                },
                {
                    "la1": "coal",
                    "ha1": "3",
                    "ba1": "7.4",
                    "ma1": "'needed'",
                    "la": "lala",
                },
                {
                    "la1": None,
                    "ha1": "2",
                    "ba1": "6.5",
                    "ma1": "'n/a'",
                    "la": "lala",
                },
                {
                    "la1": None,
                    "ha1": None,
                    "ba1": None,
                    "ma1": None,
                    "la": "lala",
                },
            ]
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurlblank,
                headers=1,
                dict_form=True,
                ignore_blank_rows=False,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            assert headers == expected_headers
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurlblank,
                headers=1,
                dict_form=True,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            assert headers == expected_headers
            del expected_dicts[4]
            del expected_dicts[1]
            assert list(iterator) == expected_dicts

            def testfn(headers, row):
                row["la"] = "lala"
                if row["ha1"] == "3":
                    return None
                return row

            headers, iterator = downloader.get_tabular_rows(
                fixtureprocessurlblank,
                headers=1,
                dict_form=True,
                header_insertions=[(2, "la")],
                row_function=testfn,
            )
            assert headers == expected_headers
            del expected_dicts[1]
            assert list(iterator) == expected_dicts

            with pytest.raises(DownloadError):
                downloader.get_tabular_rows(fixtureprocessurl, headers=None)

    def test_get_tabular_rows_xls(self, fixturexlsurl):
        with Download() as downloader:
            headers, iterator = downloader.get_tabular_rows(
                fixturexlsurl, format="xls", headers=4
            )
            assert headers == [
                "Country Name",
                "Country Code",
                "Indicator Name",
                "Indicator Code",
                "Year",
                "Value",
            ]
            rows = list(iterator)
            assert rows[0] == [
                "Aruba",
                "ABW",
                "Population, total",
                "SP.POP.TOTL",
                1960,
                54211,
            ]
            assert rows[-1] == [
                "Zimbabwe",
                "ZWE",
                "Population, total",
                "SP.POP.TOTL",
                2019,
                14645468,
            ]

    def test_get_tabular_rows_xlsx(self, fixturexlsxurl):
        with Download() as downloader:
            headers, iterator = downloader.get_tabular_rows(
                fixturexlsxurl, format="xlsx", sheet="Trend", headers=[7, 8]
            )
            assert headers[1:222] == [
                "ISO",
                "Countries and areas",
                "UNICEF Regions",
                "UN Regions",
                "WHO Regions",
                "World Bank Income Groups",
                "Survey Years",
                "Year*",
                "Short Source",
                "Full Source Title",
                "Latest Estimate",
                "Estimate Type",
                "National Point Estimate",
                "National Lower Limit",
                "National Upper Limit",
                "National Sample Size",
                "National Footnote",
                "Region 1 Point Estimate",
                "Region 1 Lower Limit",
                "Region 1 Upper Limit",
                "Region 1 Sample Size",
                "Region 1 Region Name",
                "Region 1 Footnote",
                "Region 2 Point Estimate",
                "Region 2 Lower Limit",
                "Region 2 Upper Limit",
                "Region 2 Sample Size",
                "Region 2 Region Name",
                "Region 2 Footnote",
                "Region 3 Point Estimate",
                "Region 3 Lower Limit",
                "Region 3 Upper Limit",
                "Region 3 Sample Size",
                "Region 3 Region Name",
                "Region 3 Footnote",
                "Region 4 Point Estimate",
                "Region 4 Lower Limit",
                "Region 4 Upper Limit",
                "Region 4 Sample Size",
                "Region 4 Region Name",
                "Region 4 Footnote",
                "Region 5 Point Estimate",
                "Region 5 Lower Limit",
                "Region 5 Upper Limit",
                "Region 5 Sample Size",
                "Region 5 Region Name",
                "Region 5 Footnote",
                "Region 6 Point Estimate",
                "Region 6 Lower Limit",
                "Region 6 Upper Limit",
                "Region 6 Sample Size",
                "Region 6 Region Name",
                "Region 6 Footnote",
                "Region 7 Point Estimate",
                "Region 7 Lower Limit",
                "Region 7 Upper Limit",
                "Region 7 Sample Size",
                "Region 7 Region Name",
                "Region 7 Footnote",
                "Region 8 Point Estimate",
                "Region 8 Lower Limit",
                "Region 8 Upper Limit",
                "Region 8 Sample Size",
                "Region 8 Region Name",
                "Region 8 Footnote",
                "Region 9 Point Estimate",
                "Region 9 Lower Limit",
                "Region 9 Upper Limit",
                "Region 9 Sample Size",
                "Region 9 Region Name",
                "Region 9 Footnote",
                "Region 10 Point Estimate",
                "Region 10 Lower Limit",
                "Region 10 Upper Limit",
                "Region 10 Sample Size",
                "Region 10 Region Name",
                "Region 10 Footnote",
                "Region 11 Point Estimate",
                "Region 11 Lower Limit",
                "Region 11 Upper Limit",
                "Region 11 Sample Size",
                "Region 11 Region Name",
                "Region 11 Footnote",
                "Region 12 Point Estimate",
                "Region 12 Lower Limit",
                "Region 12 Upper Limit",
                "Region 12 Sample Size",
                "Region 12 Region Name",
                "Region 12 Footnote",
                "Region 13 Point Estimate",
                "Region 13 Lower Limit",
                "Region 13 Upper Limit",
                "Region 13 Sample Size",
                "Region 13 Region Name",
                "Region 13 Footnote",
                "Region 14 Point Estimate",
                "Region 14 Lower Limit",
                "Region 14 Upper Limit",
                "Region 14 Sample Size",
                "Region 14 Region Name",
                "Region 14 Footnote",
                "Region 15 Point Estimate",
                "Region 15 Lower Limit",
                "Region 15 Upper Limit",
                "Region 15 Sample Size",
                "Region 15 Region Name",
                "Region 15 Footnote",
                "Region 16 Point Estimate",
                "Region 16 Lower Limit",
                "Region 16 Upper Limit",
                "Region 16 Sample Size",
                "Region 16 Region Name",
                "Region 16 Footnote",
                "Region 17 Point Estimate",
                "Region 17 Lower Limit",
                "Region 17 Upper Limit",
                "Region 17 Sample Size",
                "Region 17 Region Name",
                "Region 17 Footnote",
                "Region 18 Point Estimate",
                "Region 18 Lower Limit",
                "Region 18 Upper Limit",
                "Region 18 Sample Size",
                "Region 18 Region Name",
                "Region 18 Footnote",
                "Region 19 Point Estimate",
                "Region 19 Lower Limit",
                "Region 19 Upper Limit",
                "Region 19 Sample Size",
                "Region 19 Region Name",
                "Region 19 Footnote",
                "Region 20 Point Estimate",
                "Region 20 Lower Limit",
                "Region 20 Upper Limit",
                "Region 20 Sample Size",
                "Region 20 Region Name",
                "Region 20 Footnote",
                "Region 21 Point Estimate",
                "Region 21 Lower Limit",
                "Region 21 Upper Limit",
                "Region 21 Sample Size",
                "Region 21 Region Name",
                "Region 21 Footnote",
                "Region 22 Point Estimate",
                "Region 22 Lower Limit",
                "Region 22 Upper Limit",
                "Region 22 Sample Size",
                "Region 22 Region Name",
                "Region 22 Footnote",
                "Region 23 Point Estimate",
                "Region 23 Lower Limit",
                "Region 23 Upper Limit",
                "Region 23 Sample Size",
                "Region 23 Region Name",
                "Region 23 Footnote",
                "Region 24 Point Estimate",
                "Region 24 Lower Limit",
                "Region 24 Upper Limit",
                "Region 24 Sample Size",
                "Region 24 Region Name",
                "Region 24 Footnote",
                "Region 25 Point Estimate",
                "Region 25 Lower Limit",
                "Region 25 Upper Limit",
                "Region 25 Sample Size",
                "Region 25 Region Name",
                "Region 25 Footnote",
                "Region 26 Point Estimate",
                "Region 26 Lower Limit",
                "Region 26 Upper Limit",
                "Region 26 Sample Size",
                "Region 26 Region Name",
                "Region 26 Footnote",
                "Region 27 Point Estimate",
                "Region 27 Lower Limit",
                "Region 27 Upper Limit",
                "Region 27 Sample Size",
                "Region 27 Region Name",
                "Region 27 Footnote",
                "Region 28 Point Estimate",
                "Region 28 Lower Limit",
                "Region 28 Upper Limit",
                "Region 28 Sample Size",
                "Region 28 Region Name",
                "Region 28 Footnote",
                "Region 29 Point Estimate",
                "Region 29 Lower Limit",
                "Region 29 Upper Limit",
                "Region 29 Sample Size",
                "Region 29 Region Name",
                "Region 29 Footnote",
                "Region 30 Point Estimate",
                "Region 30 Lower Limit",
                "Region 30 Upper Limit",
                "Region 30 Sample Size",
                "Region 30 Region Name",
                "Region 30 Footnote",
                "Region 31 Point Estimate",
                "Region 31 Lower Limit",
                "Region 31 Upper Limit",
                "Region 31 Sample Size",
                "Region 31 Region Name",
                "Region 31 Footnote",
                "Region 32 Point Estimate",
                "Region 32 Lower Limit",
                "Region 32 Upper Limit",
                "Region 32 Sample Size",
                "Region 32 Region Name",
                "Region 32 Footnote",
                "Region 33 Point Estimate",
                "Region 33 Lower Limit",
                "Region 33 Upper Limit",
                "Region 33 Sample Size",
                "Region 33 Region Name",
                "Region 33 Footnote",
                "Region 34 Point Estimate",
                "Region 34 Lower Limit",
                "Region 34 Upper Limit",
                "Region 34 Sample Size",
                "Region 34 Region Name",
                "Region 34 Footnote",
            ]
            rows = list(iterator)
            assert rows[0][1:17] == [
                "AFG",
                "Afghanistan",
                "SA",
                "Asia",
                "EMRO",
                "Low Income",
                "2004",
                2004,
                "NNS",
                "Summary report of the national nutrition survey, 2004. Kabul, Islamic "
                "Republic of Afghanistan: Ministry of Public Health and UNICEF, 2005.",
                "Historical Trend",
                "External Reanalysis",
                3.5,
                None,
                None,
                946,
            ]
            assert rows[-1][1:113] == [
                "PSE",
                "State of Palestine",
                "MENA",
                "Asia",
                "Not Classified",
                "Lower Middle Income",
                "2014",
                2014,
                "MICS",
                "Palestinian Multiple Indicator Cluster Survey 2014,  Final Report, Ramallah, "
                "Palestine",
                "Latest Source",
                "Reanalyzed",
                0.3240246,
                0.2182891,
                0.4807297,
                6906.391,
                None,
                0.9850393,
                0.3510135,
                2.73288,
                274.0501,
                "Bethlehem",
                None,
                0.2285949,
                0.0331941,
                1.556335,
                451.0902,
                "Deir El-Balah",
                None,
                0,
                0,
                0,
                1204.021,
                "Gaza",
                None,
                0.379586,
                0.1477162,
                0.9718789,
                963.5389,
                "Hebron",
                None,
                0.9127916,
                0.3687683,
                2.241327,
                414.6011,
                "Jenin",
                None,
                0.9302664,
                0.1729868,
                4.841876,
                75.54012,
                "Jericho and Al Aghwar",
                None,
                1.340861,
                0.6852518,
                2.607252,
                479.7003,
                "Jerusalem",
                None,
                0,
                0,
                0,
                645.629,
                "Khan Yunis",
                None,
                0,
                0,
                0,
                450.1119,
                "Nablus",
                None,
                0.1555962,
                0.022686,
                1.058937,
                657.3873,
                "North Gaza",
                None,
                0.7926489,
                0.1494378,
                4.090945,
                140.6539,
                "Qalqiliya",
                None,
                0,
                0,
                0,
                459.5546,
                "Rafah",
                None,
                0.2857052,
                0.040781,
                1.97258,
                331.3463,
                "Ramallah & Al-Bireh",
                None,
                0,
                0,
                0,
                97.44475,
                "Salfit",
                None,
                0,
                0,
                0,
                55.42068,
                "Tubas",
                None,
                0.4782128,
                0.0758192,
                2.953107,
                206.3006,
                "Tulkarm",
            ]

    def test_get_tabular_rows_xlsx2csv(self, fixtureurlexcel):
        expected_headers = [
            "GWNO",
            "EVENT_ID_CNTY",
            "EVENT_ID_NO_CNTY",
            "EVENT_DATE",
            "YEAR",
            "TIME_PRECISION",
            "EVENT_TYPE",
            "ACTOR1",
            "ALLY_ACTOR_1",
            "INTER1",
            "ACTOR2",
            "ALLY_ACTOR_2",
            "INTER2",
            "INTERACTION",
            "COUNTRY",
            "ADMIN1",
            "ADMIN2",
            "ADMIN3",
            "LOCATION",
            "LATITUDE",
            "LONGITUDE",
            "GEO_PRECISION",
            "SOURCE",
            "NOTES",
            "FATALITIES",
        ]

        expected_row = [
            "615",
            "1416RTA",
            None,
            "18/04/2001",
            "2001",
            "1",
            "Violence against civilians",
            "Police Forces of Algeria (1999-)",
            None,
            "1",
            "Civilians (Algeria)",
            "Berber Ethnic Group (Algeria)",
            "7",
            "17",
            "Algeria",
            "Tizi Ouzou",
            "Beni-Douala",
            None,
            "Beni Douala",
            "36.61954",
            "4.08282",
            "1",
            "Associated Press Online",
            "A Berber student was shot while in police custody at a police station in "
            "Beni Douala. He later died on Apr.21.",
            "1",
        ]

        with Download() as downloader:
            headers, iterator = downloader.get_tabular_rows(
                fixtureurlexcel,
                format="xlsx",
                xlsx2csv=True,
            )
            assert headers == expected_headers
            assert list(iterator)[0] == expected_row

            headers, iterator = downloader.get_tabular_rows(
                fixtureurlexcel,
                format="xlsx",
                xlsx2csv=True,
                sheet="test_data",
            )
            assert headers == expected_headers
            assert list(iterator)[0] == expected_row

    def test_get_tabular_rows_json(self, fixturejsonurl):
        with Download() as downloader:
            headers, iterator = downloader.get_tabular_rows(
                fixturejsonurl, format="json"
            )
            assert headers == ["Country Code", "Country Name", "Population"]
            assert list(iterator) == [
                ["#country+code", "#country+name", "#population"],
                ["AFG", "Afghanistan", 38041754],
            ]

    def test_download_tabular_rows_as_dicts(self, fixtureprocessurl):
        with Download() as downloader:
            result = downloader.download_tabular_rows_as_dicts(
                fixtureprocessurl, headers=2
            )
            assert result == {
                "coal": {
                    "header2": "3",
                    "header3": "7.4",
                    "header4": "'needed'",
                },
                "gas": {"header2": "2", "header3": "6.5", "header4": "'n/a'"},
            }
            result = downloader.download_tabular_rows_as_dicts(
                fixtureprocessurl, headers=2, keycolumn=2
            )
            assert result == {
                "2": {"header1": "gas", "header3": "6.5", "header4": "'n/a'"},
                "3": {
                    "header1": "coal",
                    "header3": "7.4",
                    "header4": "'needed'",
                },
            }

    def test_download_tabular_cols_as_dicts(self, fixtureprocessurl):
        with Download() as downloader:
            result = downloader.download_tabular_cols_as_dicts(
                fixtureprocessurl, headers=2
            )
            assert result == {
                "header2": {"coal": "3", "gas": "2"},
                "header3": {"coal": "7.4", "gas": "6.5"},
                "header4": {"coal": "'needed'", "gas": "'n/a'"},
            }
            result = downloader.download_tabular_cols_as_dicts(
                fixtureprocessurl, headers=2, keycolumn=2
            )
            assert result == {
                "header1": {"3": "coal", "2": "gas"},
                "header3": {"3": "7.4", "2": "6.5"},
                "header4": {"3": "'needed'", "2": "'n/a'"},
            }

    def test_get_column_positions(self):
        assert Download.get_column_positions(["a", "b", "c"]) == {
            "a": 0,
            "b": 1,
            "c": 2,
        }

    def test_generate_downloaders(self, downloaders):
        downloader1 = Download.get_downloader()
        downloader2 = Download.get_downloader("test")
        assert_downloaders(downloader1, downloader2, downloaders)
