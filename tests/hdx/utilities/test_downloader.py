# -*- coding: UTF-8 -*-
"""Downloader Tests"""
import re
from collections import OrderedDict
from os import remove
from os.path import join, abspath
from shutil import rmtree, copytree
from tempfile import gettempdir

import pytest

from hdx.utilities.downloader import Download, DownloadError
from hdx.utilities.session import SessionError


class TestDownloader:
    downloaderfoldername = 'downloader'

    @pytest.fixture(scope='class')
    def downloaderfolder(self, fixturesfolder):
        return join(fixturesfolder, self.downloaderfoldername)

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

    def test_init(self, downloaderfolder):
        basicauthfile = join(downloaderfolder, 'basicauth.txt')
        with Download(auth=('u', 'p')) as downloader:
            assert downloader.session.auth == ('u', 'p')
        with Download(basic_auth='Basic dXNlcjpwYXNz') as downloader:
            assert downloader.session.auth == ('user', 'pass')
        with Download(basic_auth_file=basicauthfile) as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), basic_auth='Basic xxxxxxxxxxxxxxxx')
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), basic_auth_file=join('lala', 'lala.txt'))
        with pytest.raises(SessionError):
            Download(basic_auth='Basic dXNlcjpwYXNz', basic_auth_file=join('lala', 'lala.txt'))
        extraparamsyamltree = join(downloaderfolder, 'extra_params_tree.yml')
        with pytest.raises(SessionError):
            Download(auth=('u', 'p'), extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        with pytest.raises(SessionError):
            Download(basic_auth='Basic dXNlcjpwYXNz', extra_params_yaml=extraparamsyamltree,
                     extra_params_lookup='mykey')
        with pytest.raises(SessionError):
            Download(basic_auth_file=basicauthfile, extra_params_yaml=extraparamsyamltree, extra_params_lookup='mykey')
        with pytest.raises(IOError):
            Download(basic_auth_file='NOTEXIST')
        extraparamsjson = join(downloaderfolder, 'extra_params.json')
        extraparamsyaml = join(downloaderfolder, 'extra_params.yml')
        test_url = 'http://www.lalala.com/lala'
        with Download(basic_auth_file=basicauthfile, extra_params_dict={'key1': 'val1'}) as downloader:
            assert downloader.session.auth == ('testuser', 'testpass')
            assert downloader.get_full_url(test_url) == '%s?key1=val1' % test_url
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
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_json=extraparamsjson)
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_yaml=extraparamsyaml)
        with pytest.raises(SessionError):
            Download(extra_params_dict={'key1': 'val1'}, extra_params_yaml=extraparamsyamltree,
                     extra_params_lookup='mykey')
        with pytest.raises(IOError):
            Download(extra_params_json='NOTEXIST')

    def test_get_url_for_get(self):
        assert Download.get_url_for_get('http://www.lala.com/hdfa?a=3&b=4', OrderedDict(
            [('c', 'e'), ('d', 'f')])) == 'http://www.lala.com/hdfa?a=3&b=4&c=e&d=f'

    def test_get_url_params_for_post(self):
        assert Download.get_url_params_for_post('http://www.lala.com/hdfa?a=3&b=4',
                                                OrderedDict([('c', 'e'), ('d', 'f')])) == (
               'http://www.lala.com/hdfa', OrderedDict([('a', '3'), ('b', '4'), ('c', 'e'), ('d', 'f')]))

    def test_setup_stream(self, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup('NOTEXIST://NOTEXIST.csv')
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.setup(fixturenotexistsurl)
        with Download() as downloader:
            downloader.setup(fixtureurl)
            headers = downloader.response.headers
            assert headers['Content-Length'] == '728'
        with Download() as downloader:
            downloader.setup(postfixtureurl, post=True)
            headers = downloader.response.headers
            assert bool(re.match(r'3[56]\d', headers['Content-Length'])) is True
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

    def test_download_file(self, tmpdir, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        tmpdir = str(tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file('NOTEXIST://NOTEXIST.csv', tmpdir)
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download_file(fixturenotexistsurl)
        with Download() as downloader:
            f = downloader.download_file(fixtureurl, folder=tmpdir)
            fpath = abspath(f)
            remove(f)
            assert fpath == abspath(join(tmpdir, 'test_data.csv'))
            filename = 'myfilename.txt'
            f = downloader.download_file(fixtureurl, folder=tmpdir, filename=filename)
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

    def test_download(self, fixtureurl, fixturenotexistsurl, getfixtureurl, postfixtureurl):
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download('NOTEXIST://NOTEXIST.csv')
        with pytest.raises(DownloadError), Download() as downloader:
            downloader.download(fixturenotexistsurl)
        with Download() as downloader:
            result = downloader.download(fixtureurl)
            assert result.headers['Content-Length'] == '728'
            downloader.download('%s?id=10&lala=a' % getfixtureurl, post=False,
                                parameters=OrderedDict([('b', '4'), ('d', '3')]))
            assert downloader.get_json()['args'] == OrderedDict([('b', '4'), ('d', '3'), ('id', '10'), ('lala', 'a')])
            downloader.download('%s?id=3&lala=b' % postfixtureurl, post=True,
                                         parameters=OrderedDict([('a', '3'), ('c', '2')]))
            assert downloader.get_json()['form'] == OrderedDict([('a', '3'), ('c', '2'), ('id', '3'), ('lala', 'b')])

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
