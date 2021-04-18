# -*- coding: UTF-8 -*-
"""Downloader Tests"""
import copy
import re
from collections import OrderedDict
from os import remove
from os.path import join, abspath
from shutil import rmtree, copytree
from tempfile import gettempdir

import pytest
from contextlib import contextmanager

from hdx.utilities.downloader import Download, DownloadError
from hdx.utilities.session import SessionError
from hdx.utilities.useragent import UserAgent


@contextmanager
def not_raises(ExpectedException):
    try:
        yield
    except ExpectedException as error:
        raise pytest.fail('Raised exception {0} when it should not!'.format(error))

    except Exception as error:
        raise pytest.fail('An unexpected exception {0} raised.'.format(error))


class TestDownloader:
    downloaderfoldername = 'downloader'

    @pytest.fixture(scope='class', autouse=True)
    def useragent(self):
        UserAgent.set_global('test')
        yield
        UserAgent.clear_global()

    @pytest.fixture(scope='class')
    def downloaderfolder(self, fixturesfolder):
        return join(fixturesfolder, self.downloaderfoldername)

    @pytest.fixture(scope='class')
    def fixturefile(self, downloaderfolder):
        return join(downloaderfolder, 'extra_params_tree.yml')

    @pytest.fixture(scope='class')
    def fixtureurl(self):
        return 'https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/master/tests/fixtures/test_data.csv'

    @pytest.fixture(scope='class')
    def getfixtureurl(self):
        return 'http://httpbin.org/get'

    @pytest.fixture(scope='class')
    def postfixtureurl(self):
        return 'http://httpbin.org/post'

    @pytest.fixture(scope='class')
    def fixturenotexistsurl(self):
        return 'https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/master/tests/fixtures/NOTEXIST.csv'

    @pytest.fixture(scope='class')
    def fixtureprocessurl(self):
        return 'https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/master/tests/fixtures/downloader/test_csv_processing.csv?a=1'

    @pytest.fixture(scope='class')
    def fixtureprocessurlblank(self):
        return 'https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/master/tests/fixtures/downloader/test_csv_processing_blanks.csv?a=1'

    def test_get_path_for_url(self, tmpdir, fixtureurl, configfolder, downloaderfolder):
        tmpdir = str(tmpdir)
        filename = 'test_data.csv'
        path = Download.get_path_for_url(fixtureurl, configfolder)
        assert abspath(path) == abspath(join(configfolder, filename))
        path = Download.get_path_for_url(fixtureurl, downloaderfolder)
        assert abspath(path) == abspath(join(downloaderfolder, 'test_data3.csv'))
        testfolder = join(tmpdir, self.downloaderfoldername)
        rmtree(testfolder, ignore_errors=True)
        copytree(downloaderfolder, testfolder)
        path = Download.get_path_for_url(fixtureurl, testfolder, overwrite=True)
        assert abspath(path) == abspath(join(testfolder, filename))
        rmtree(testfolder)
        filename = 'myfilename.txt'
        path = Download.get_path_for_url(fixtureurl, filename=filename)
        assert abspath(path) == abspath(join(gettempdir(), filename))
        path = Download.get_path_for_url(fixtureurl, downloaderfolder, filename)
        assert abspath(path) == abspath(join(downloaderfolder, filename))

    def test_init(self, monkeypatch, downloaderfolder):
        basicauthfile = join(downloaderfolder, 'basicauth.txt')
        with Download(auth=('u', 'p')) as downloader:
            assert downloader.session.auth == ('u', 'p')
        basicauth = 'Basic dXNlcjpwYXNz'
        with Download(basic_auth=basicauth) as downloader:
            assert downloader.session.auth == ('user', 'pass')
        with Download(basic_auth_file=basicauthfile) as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
        extraparamsyamltree = join(downloaderfolder, 'extra_params_tree.yml')
        with Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey') as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
        monkeypatch.setenv('BASIC_AUTH', basicauth)
        with Download() as downloader:
            assert downloader.session.auth == ('user', 'pass')
        with pytest.raises(SessionError):
            Download(basic_auth='12345')
        with pytest.raises(SessionError):
            Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        monkeypatch.delenv('BASIC_AUTH')
        with pytest.raises(SessionError):
            Download(basic_auth=basicauth, extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), basic_auth='Basic xxxxxxxxxxxxxxxx')
        extraparamsjson = join(downloaderfolder, 'extra_params.json')
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), basic_auth_file=extraparamsjson)
        with pytest.raises(SessionError):
            Download(basic_auth='Basic dXNlcjpwYXNz', basic_auth_file=extraparamsjson)
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        with pytest.raises(SessionError):
            Download(basic_auth_file=basicauthfile, extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        with pytest.raises(SessionError):
            Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='missingkey')
        with pytest.raises(IOError):
            Download(basic_auth_file='NOTEXIST')
        extraparamsyaml = join(downloaderfolder, 'extra_params.yml')
        test_url = 'http://www.lalala.com/lala'
        with Download(basic_auth_file=basicauthfile, extra_params_dict={'key1': 'val1'}) as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
            assert downloader.get_full_url(test_url) == '%s?key1=val1' % test_url
        key = 'Authorization'
        value = 'lala'
        with Download(headers={key: value}) as downloader:
            assert key in downloader.session.headers
            assert downloader.session.headers.get(key) == value
        with Download(extra_params_json=extraparamsjson) as downloader:
            full_url = downloader.get_full_url(test_url)
            assert 'param_1=value+1' in full_url
            assert 'param_2=value_2' in full_url
            assert 'param_3=12' in full_url
        with Download(extra_params_yaml=extraparamsyaml) as downloader:
            full_url = downloader.get_full_url(test_url)
            assert 'param1=value1' in full_url
            assert 'param2=value+2' in full_url
            assert 'param3=10' in full_url
        with Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey') as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
            full_url = downloader.get_full_url(test_url)
            assert 'param1=value+1' in full_url
            assert 'param2=value2' in full_url
            assert 'param3=11' in full_url
            assert 'basic_auth' not in full_url
        monkeypatch.setenv('EXTRA_PARAMS', 'param1=value2+3,param2=value3+7')
        with Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey') as downloader:
            assert downloader.session.auth is None
            full_url = downloader.get_full_url(test_url)
            assert 'param1=value2%2B3' in full_url
            assert 'param2=value3%2B7' in full_url
            assert 'param3=11' not in full_url
            assert 'basic_auth' not in full_url
        with Download(extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey', use_env=False) as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
            full_url = downloader.get_full_url(test_url)
            assert 'param1=value+1' in full_url
            assert 'param2=value2' in full_url
            assert 'param3=11' in full_url
            assert 'basic_auth' not in full_url
        monkeypatch.delenv('EXTRA_PARAMS')
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_json=extraparamsjson)
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_yaml=extraparamsyaml)
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_yaml=extraparamsyamltree,
                     extra_params_lookup='mykey')
        with pytest.raises(IOError):
            Download(extra_params_json='NOTEXIST')
        with pytest.raises(IOError):
            Download(extra_params_yaml='NOTEXIST')
        with not_raises(IOError):
            Download(extra_params_json='NOTEXIST', fail_on_missing_file=False)
            Download(extra_params_yaml='NOTEXIST', fail_on_missing_file=False)
            Download(basic_auth_file='NOTEXIST', fail_on_missing_file=False)

    def test_get_url_for_get(self):
        assert Download.get_url_for_get('http://www.lala.com/hdfa?a=3&b=4', OrderedDict(
            [('c', 'e'), ('d', 'f')])) == 'http://www.lala.com/hdfa?a=3&b=4&c=e&d=f'

    def test_get_url_params_for_post(self):
        assert Download.get_url_params_for_post('http://www.lala.com/hdfa?a=3&b=4',
                                                OrderedDict([('c', 'e'), ('d', 'f')])) == (
                   'http://www.lala.com/hdfa', OrderedDict([('a', '3'), ('b', '4'), ('c', 'e'), ('d', 'f')]))

    def test_hxl_row(self):
        headers = ['a', 'b', 'c']
        hxltags = {'b': '#b', 'c': '#c'}
        assert Download.hxl_row(headers, hxltags) == ['', '#b', '#c']
        assert Download.hxl_row(headers, hxltags, dict_form=True) == {'a': '', 'b': '#b', 'c': '#c'}
        assert Download.hxl_row(headers, dict()) == ['', '', '']
        assert Download.hxl_row([], hxltags) == list()

    def test_setup_stream(self, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup('NOTEXIST://NOTEXIST.csv')
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup(fixturenotexistsurl)
        with Download() as downloader:
            downloader.setup(fixtureurl)
            headers = downloader.response.headers
            assert bool(re.match(r'7\d\d', headers['Content-Length'])) is True
        with Download() as downloader:
            downloader.setup(postfixtureurl, post=True)
            headers = downloader.response.headers
            assert bool(re.match(r'4\d\d', headers['Content-Length'])) is True
            downloader.setup('%s?id=10&lala=a' % getfixtureurl, post=False,
                             parameters=OrderedDict([('b', '4'), ('d', '3')]))
            assert downloader.get_json()['args'] == OrderedDict([('b', '4'), ('d', '3'), ('id', '10'), ('lala', 'a')])
            downloader.setup('%s?id=3&lala=b' % postfixtureurl, post=True,
                             parameters=OrderedDict([('a', '3'), ('c', '2')]))
            assert downloader.get_json()['form'] == OrderedDict([('a', '3'), ('c', '2'), ('id', '3'), ('lala', 'b')])

    def test_hash_stream(self, fixtureurl):
        with Download() as downloader:
            downloader.setup(fixtureurl)
            md5hash = downloader.hash_stream(fixtureurl)
            assert md5hash == 'da9db35a396cca10c618f6795bdb9ff2'

    def test_download_file(self, tmpdir, fixturefile, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        tmpdir = str(tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file('NOTEXIST://NOTEXIST.csv', tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(fixturenotexistsurl)
        filename = 'myfilename.txt'
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(fixturefile, folder=tmpdir, path=join(tmpdir, filename))
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(fixturefile, filename=filename, path=join(tmpdir, filename))
        with Download() as downloader:
            f = downloader.download_file(fixturefile, folder=tmpdir)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, 'extra_params_tree.yml'))
            f = downloader.download_file(fixtureurl, folder=tmpdir)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, 'test_data.csv'))
            f = downloader.download_file(fixtureurl, folder=tmpdir, filename=filename)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file(fixtureurl, path=join(tmpdir, filename), overwrite=True)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file('%s?id=10&lala=a' % getfixtureurl, post=False,
                                         parameters=OrderedDict([('b', '4'), ('d', '3')]), folder=tmpdir,
                                         filename=filename)
            fpath = abspath(f)
            with open(fpath, 'rt') as fi:
                text = fi.read()
                assert '"id": "10"' in text
                assert '"lala": "a"' in text
                assert '"b": "4"' in text
                assert '"d": "3"' in text
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))
            f = downloader.download_file('%s?id=3&lala=b' % postfixtureurl, post=True,
                                         parameters=OrderedDict([('a', '3'), ('c', '2')]), folder=tmpdir,
                                         filename=filename)
            fpath = abspath(f)
            with open(fpath, 'rt') as fi:
                text = fi.read()
                assert '"id": "3"' in text
                assert '"lala": "b"' in text
                assert '"a": "3"' in text
                assert '"c": "2"' in text
            remove(f)
            assert fpath == abspath(join(tmpdir, filename))

    def test_download(self, fixturefile, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download('NOTEXIST://NOTEXIST.csv')
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download(fixturenotexistsurl)
        with Download() as downloader:
            result = downloader.download(fixtureurl)
            assert bool(re.match(r'7\d\d', result.headers['Content-Length'])) is True
            downloader.download('%s?id=10&lala=a' % getfixtureurl, post=False,
                                parameters=OrderedDict([('b', '4'), ('d', '3')]))
            assert downloader.get_json()['args'] == OrderedDict([('b', '4'), ('d', '3'), ('id', '10'), ('lala', 'a')])
            downloader.download('%s?id=3&lala=b' % postfixtureurl, post=True,
                                parameters=OrderedDict([('a', '3'), ('c', '2')]))
            assert downloader.get_json()['form'] == OrderedDict([('a', '3'), ('c', '2'), ('id', '3'), ('lala', 'b')])
        with Download(rate_limit={'calls': 1, 'period': 0.1}) as downloader:
            downloader.download('%s?id=10&lala=a' % getfixtureurl, post=False,
                                parameters=OrderedDict([('b', '4'), ('d', '3')]))
            assert downloader.get_json()['args'] == OrderedDict([('b', '4'), ('d', '3'), ('id', '10'), ('lala', 'a')])
            downloader.download(fixturefile)
            assert downloader.get_yaml()['mykey'] == OrderedDict([('param1', 'value 1'), ('param2', 'value2'), ('param3', 11), ('basic_auth', 'Basic dGVzdHVzZXI6dGVzdHBhc3M=')])

    def test_download_tabular_key_value(self, fixtureurl, fixtureprocessurl):
        with Download() as downloader:
            result = downloader.download_tabular_key_value(fixtureurl, file_type='csv')
            assert result == {'615': '2231RTA', 'GWNO': 'EVENT_ID_CNTY'}
            result = downloader.download_tabular_key_value(fixtureprocessurl, headers=2)
            assert result == {'coal': '3', 'gas': '2'}
            with pytest.raises(DownloadError):
                downloader.download_tabular_key_value('NOTEXIST://NOTEXIST.csv')

    @staticmethod
    def fix_strings(result):  # This isn't needed when I run locally but is when run in Travis!
        for x in result:
            for y in result[x]:
                result[x][y] = result[x][y].replace("'", '')

    def test_get_tabular_rows_as_list(self, fixtureprocessurl):
        with Download() as downloader:
            rows = list(downloader.get_tabular_rows_as_list(fixtureprocessurl))
            assert rows == [['la1', 'ha1', 'ba1', 'ma1'], ['header1', 'header2', 'header3', 'header4'],
                            ['coal', '3', '7.4', 'needed'], ['gas', '2', '6.5', 'n/a']]

    def test_get_tabular_rows(self, fixtureprocessurl, fixtureprocessurlblank):
        with Download() as downloader:
            expected = [['la1', 'ha1', 'ba1', 'ma1'], ['header1', 'header2', 'header3', 'header4'],
                        ['coal', '3', '7.4', 'needed'], ['gas', '2', '6.5', 'n/a']]
            expected_headers = expected[0]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl)
            assert headers == expected_headers
            assert list(iterator) == expected[1:]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank)
            assert headers == expected_headers
            blank_expected = copy.deepcopy(expected[1:])
            blank_expected[2][0] = ''
            assert list(iterator) == blank_expected
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank, ignore_blank_rows=False)
            assert headers == expected_headers
            blank_expected.append(list())
            blank_expected.insert(1, list())
            assert list(iterator) == blank_expected
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=1)
            assert headers == expected_headers
            assert list(iterator) == expected[1:]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=2)
            assert headers == expected[1]
            assert list(iterator) == expected[2:]
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=[1, 2])
            assert headers == ['la1 header1', 'ha1 header2', 'ba1 header3', 'ma1 header4']
            assert list(iterator) == expected[2:]
            myheaders = ['a', 'b', 'c', 'd']
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=myheaders)
            assert headers == myheaders
            assert list(iterator) == expected
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=1, dict_form=True)
            assert headers == expected_headers
            expected_dicts = [{'la1': 'header1', 'ha1': 'header2', 'ba1': 'header3', 'ma1': 'header4'},
                              {'la1': 'coal', 'ha1': '3', 'ba1': '7.4', 'ma1': 'needed'},
                              {'la1': 'gas', 'ha1': '2', 'ba1': '6.5', 'ma1': 'n/a'}]
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=3, dict_form=True)
            assert headers == expected[2]
            expected_dicts = [{'coal': 'gas', '3': '2', '7.4': '6.5', 'needed': 'n/a'}]
            assert list(iterator) == expected_dicts

            def testfn(headers, row):
                row.insert(2, 'lala')
                return row

            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=3,
                                                            header_insertions=[(2, 'la')], row_function=testfn)
            expected_headers = ['coal', '3', 'la', '7.4', 'needed']
            assert headers == expected_headers
            assert list(iterator) == [['gas', '2', 'lala', '6.5', 'n/a']]

            def testfn(headers, row):
                row['la'] = 'lala'
                return row

            headers, iterator = downloader.get_tabular_rows(fixtureprocessurl, headers=3, dict_form=True,
                                                            header_insertions=[(2, 'la')], row_function=testfn)
            assert headers == expected_headers
            expected_dicts[0]['la'] = 'lala'
            assert list(iterator) == expected_dicts

            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank, headers=1, dict_form=True, ignore_blank_rows=False,
                                                            header_insertions=[(2, 'la')], row_function=testfn)
            expected_headers = ['la1', 'ha1', 'la', 'ba1', 'ma1']
            assert headers == expected_headers

            expected_dicts = [{'la1': 'header1', 'ha1': 'header2', 'ba1': 'header3', 'ma1': 'header4', 'la': 'lala'},
                              {'la': 'lala'},
                              {'la1': 'coal', 'ha1': '3', 'ba1': '7.4', 'ma1': 'needed', 'la': 'lala'},
                              {'la1': '', 'ha1': '2', 'ba1': '6.5', 'ma1': 'n/a', 'la': 'lala'},
                              {'la': 'lala'}]
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank, headers=1, dict_form=True,
                                                            ignore_blank_rows=False, header_insertions=[(2, 'la')],
                                                            row_function=testfn)
            assert headers == expected_headers
            assert list(iterator) == expected_dicts
            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank, headers=1, dict_form=True,
                                                            header_insertions=[(2, 'la')], row_function=testfn)
            assert headers == expected_headers
            del expected_dicts[4]
            del expected_dicts[1]
            assert list(iterator) == expected_dicts

            def testfn(headers, row):
                row['la'] = 'lala'
                if row['ha1'] == '3':
                    return None
                return row

            headers, iterator = downloader.get_tabular_rows(fixtureprocessurlblank, headers=1, dict_form=True,
                                                            header_insertions=[(2, 'la')], row_function=testfn)
            assert headers == expected_headers
            del expected_dicts[1]
            assert list(iterator) == expected_dicts

            with pytest.raises(DownloadError):
                downloader.get_tabular_rows(fixtureprocessurl, headers=None)

    def test_download_tabular_rows_as_dicts(self, fixtureprocessurl):
        with Download() as downloader:
            result = downloader.download_tabular_rows_as_dicts(fixtureprocessurl, headers=2)
            self.fix_strings(result)
            assert result == {'coal': {'header2': '3', 'header3': '7.4', 'header4': 'needed'},
                              'gas': {'header2': '2', 'header3': '6.5', 'header4': 'n/a'}}
            result = downloader.download_tabular_rows_as_dicts(fixtureprocessurl, headers=2, keycolumn=2)
            self.fix_strings(result)
            assert result == {'2': {'header1': 'gas', 'header3': '6.5', 'header4': 'n/a'},
                              '3': {'header1': 'coal', 'header3': '7.4', 'header4': 'needed'}}

    def test_download_tabular_cols_as_dicts(self, fixtureprocessurl):
        with Download() as downloader:
            result = downloader.download_tabular_cols_as_dicts(fixtureprocessurl, headers=2)
            self.fix_strings(result)
            assert result == {'header2': {'coal': '3', 'gas': '2'},
                              'header3': {'coal': '7.4', 'gas': '6.5'},
                              'header4': {'coal': 'needed', 'gas': 'n/a'}}
            result = downloader.download_tabular_cols_as_dicts(fixtureprocessurl, headers=2, keycolumn=2)
            self.fix_strings(result)
            assert result == {'header1': {'3': 'coal', '2': 'gas'},
                              'header3': {'3': '7.4', '2': '6.5'},
                              'header4': {'3': 'needed', '2': 'n/a'}}

    def test_get_column_positions(self):
        assert Download.get_column_positions(['a', 'b', 'c']) == {'a': 0, 'b': 1, 'c': 2}
