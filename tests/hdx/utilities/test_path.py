# -*- coding: UTF-8 -*-
"""Path Utility Tests"""
from os.path import join, exists
from shutil import rmtree
from tempfile import gettempdir

import pytest

from hdx.utilities.path import get_temp_dir, temp_dir, progress_storing_tempdir


class TestPath:
    @pytest.fixture(scope='class')
    def mytestdir(self):
        return join('haha', 'lala')

    def test_get_temp_dir(self, monkeypatch, mytestdir):
        assert get_temp_dir() == gettempdir()
        monkeypatch.setenv('TEMP_DIR', mytestdir)
        assert get_temp_dir() == mytestdir
        monkeypatch.delenv('TEMP_DIR')

    def test_temp_dir(self, monkeypatch, mytestdir):
        monkeypatch.setenv('TEMP_DIR', mytestdir)
        with temp_dir() as tempdir:
            assert tempdir == mytestdir
        monkeypatch.delenv('TEMP_DIR')

        tempfolder = 'papa'
        expected_dir = join(gettempdir(), tempfolder)

        with temp_dir(tempfolder) as tempdir:
            assert tempdir == expected_dir
        assert exists(tempdir) is False
        try:
            with temp_dir(tempfolder) as tempdir:
                assert tempdir == expected_dir
                raise ValueError('Fail!')
        except:
            pass
        assert exists(tempdir) is False

        with temp_dir(tempfolder, delete_on_success=True, delete_on_failure=True) as tempdir:
            assert tempdir == expected_dir
        assert exists(tempdir) is False
        try:
            with temp_dir(tempfolder, delete_on_success=True, delete_on_failure=True) as tempdir:
                assert tempdir == expected_dir
                raise ValueError('Fail!')
        except:
            pass
        assert exists(tempdir) is False

        with temp_dir(tempfolder, delete_on_success=False, delete_on_failure=False) as tempdir:
            assert tempdir == expected_dir
        assert exists(tempdir) is True
        rmtree(tempdir)
        try:
            with temp_dir(tempfolder, delete_on_success=False, delete_on_failure=False) as tempdir:
                assert tempdir == expected_dir
                raise ValueError('Fail!')
        except:
            pass
        assert exists(tempdir) is True

        with temp_dir(tempfolder, delete_on_success=True, delete_on_failure=False) as tempdir:
            assert tempdir == expected_dir
        assert exists(tempdir) is False
        try:
            with temp_dir(tempfolder, delete_on_success=True, delete_on_failure=False) as tempdir:
                assert tempdir == expected_dir
                raise ValueError('Fail!')
        except:
            pass
        assert exists(tempdir) is True
        rmtree(tempdir)

        with temp_dir(tempfolder, delete_on_success=False, delete_on_failure=True) as tempdir:
            assert tempdir == expected_dir
        assert exists(tempdir) is True
        rmtree(tempdir)
        try:
            with temp_dir(tempfolder, delete_on_success=False, delete_on_failure=True) as tempdir:
                assert tempdir == expected_dir
                raise ValueError('Fail!')
        except:
            pass
        assert exists(tempdir) is False

    def test_progress_storing_tempdir(self, monkeypatch):
        tempfolder = 'papa'
        expected_dir = join(gettempdir(), tempfolder)
        iterator = [{'iso3': 'AFG', 'name': 'Afghanistan'}, {'iso3': 'SDN', 'name': 'Sudan'},
                    {'iso3': 'YEM', 'name': 'Yemen'}, {'iso3': 'ZAM', 'name': 'Zambia'}]
        result = list()
        for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(tempdir) is True
            assert tempdir == expected_dir
            result.append(nextdict)
        assert result == iterator
        assert exists(expected_dir) is False

        monkeypatch.setenv('WHERETOSTART', 'SDN')
        result = list()
        for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(tempdir) is True
            assert tempdir == expected_dir
            result.append(nextdict)
        assert result == iterator[1:]
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        result = list()
        for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(tempdir) is True
            assert tempdir == expected_dir
            result.append(nextdict)
        assert result == iterator[2:]
        assert exists(expected_dir) is False

        try:
            for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'RESET')
        result = list()
        for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(tempdir) is True
            assert tempdir == expected_dir
            result.append(nextdict)
        assert result == iterator
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'SDN')
        result = list()
        for tempdir, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(tempdir) is True
            assert tempdir == expected_dir
            result.append(nextdict)
        assert result == iterator[1:]
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')
