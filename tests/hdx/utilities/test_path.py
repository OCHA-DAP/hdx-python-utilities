# -*- coding: UTF-8 -*-
"""Path Utility Tests"""
import copy
from os.path import join, exists
from shutil import rmtree
from tempfile import gettempdir

import pytest

from hdx.utilities.loader import load_file_to_str
from hdx.utilities.path import get_temp_dir, temp_dir, progress_storing_tempdir, multiple_progress_storing_tempdir


class TestPath:
    @pytest.fixture(scope='class')
    def mytestdir(self):
        return join('haha', 'lala')

    def test_get_temp_dir(self, monkeypatch, mytestdir):
        assert get_temp_dir() == gettempdir()
        assert get_temp_dir('TEST') == join(gettempdir(), 'TEST')
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
        rmtree(expected_dir, ignore_errors=True)
        iterator = [{'iso3': 'AFG', 'name': 'Afghanistan'}, {'iso3': 'SDN', 'name': 'Sudan'},
                    {'iso3': 'YEM', 'name': 'Yemen'}, {'iso3': 'ZAM', 'name': 'Zambia'}]
        expected_batch_file = join(expected_dir, 'batch.txt')
        result = list()
        for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert info['folder'] == expected_dir
            expected_batch = load_file_to_str(expected_batch_file, strip=True)
            result.append(nextdict)
        assert result == iterator
        assert expected_batch == info['batch']
        assert exists(expected_dir) is False

        monkeypatch.setenv('WHERETOSTART', 'iso3=SDN')
        result = list()
        for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(info['folder']) is True
            assert info['folder'] == expected_dir
            expected_batch = load_file_to_str(expected_batch_file, strip=True)
            result.append(nextdict)
        assert result == iterator[1:]
        assert expected_batch == info['batch']
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        result = list()
        for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(info['folder']) is True
            assert info['folder'] == expected_dir
            assert info['batch'] == start_batch
            result.append(nextdict)
        assert result == iterator[2:]
        assert exists(expected_dir) is False

        try:
            for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'RESET')
        result = list()
        for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(info['folder']) is True
            assert info['folder'] == expected_dir
            assert info['batch'] != start_batch
            result.append(nextdict)
        assert result == iterator
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'iso3=SDN')
        result = list()
        for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            assert exists(info['folder']) is True
            assert info['folder'] == expected_dir
            assert info['batch'] == start_batch
            result.append(nextdict)
        assert result == iterator[1:]
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for info, nextdict in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
                if nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        monkeypatch.setenv('WHERETOSTART', 'iso3=NOTFOUND')
        found = False
        for _ in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            found = True
        assert found is False
        assert exists(expected_dir) is True
        batch = load_file_to_str(expected_batch_file, strip=True)
        assert batch == start_batch
        monkeypatch.delenv('WHERETOSTART')

        monkeypatch.setenv('WHERETOSTART', 'NOTFOUND=SDN')
        found = False
        for _ in progress_storing_tempdir(tempfolder, iterator, 'iso3'):
            found = True
        assert found is False
        assert exists(expected_dir) is True
        batch = load_file_to_str(expected_batch_file, strip=True)
        assert batch == start_batch
        monkeypatch.delenv('WHERETOSTART')

        rmtree(expected_dir, ignore_errors=True)

    def test_multiple_progress_storing_tempdir(self, monkeypatch):
        tempfolder = 'gaga'
        expected_dir = join(gettempdir(), tempfolder)
        rmtree(expected_dir, ignore_errors=True)
        iterator1 = [{'emergency_id': '911'}]
        iterator2 = [{'iso3': 'AFG', 'name': 'Afghanistan'}, {'iso3': 'SDN', 'name': 'Sudan'},
                     {'iso3': 'YEM', 'name': 'Yemen'}, {'iso3': 'ZAM', 'name': 'Zambia'}]
        iterators = [iterator1, iterator2]
        keys = ['emergency_id', 'iso3']
        results = list()
        for result in multiple_progress_storing_tempdir(tempfolder, iterators, keys, '1234'):
            results.append(copy.deepcopy(result))
        expected_results = [(0, {'folder': '/tmp/gaga/0', 'batch': '1234', 'progress': 'emergency_id=911'}, {'emergency_id': '911'}),
                            (1, {'folder': '/tmp/gaga/1', 'batch': '1234', 'progress': 'iso3=AFG'}, {'iso3': 'AFG', 'name': 'Afghanistan'}),
                            (1, {'folder': '/tmp/gaga/1', 'batch': '1234', 'progress': 'iso3=SDN'}, {'iso3': 'SDN', 'name': 'Sudan'}),
                            (1, {'folder': '/tmp/gaga/1', 'batch': '1234', 'progress': 'iso3=YEM'}, {'iso3': 'YEM', 'name': 'Yemen'}),
                            (1, {'folder': '/tmp/gaga/1', 'batch': '1234', 'progress': 'iso3=ZAM'}, {'iso3': 'ZAM', 'name': 'Zambia'})]
        assert results == expected_results
        assert exists(expected_dir) is False
        results = list()
        try:
            for result in multiple_progress_storing_tempdir(tempfolder, iterators, keys):
                results.append(copy.deepcopy(result))
                i, info, nextdict = result
                if 'iso3' in nextdict and nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        for result in expected_results:
            result[1]['batch'] = start_batch
        assert results == expected_results[:4]
        assert exists(expected_dir) is True
        result = list()
        for i, info, nextdict in multiple_progress_storing_tempdir(tempfolder, iterators, keys):
            assert exists(info['folder']) is True
            assert info['folder'] == join(expected_dir, '1')
            assert info['batch'] == start_batch
            result.append(nextdict)
        assert result == iterator2[2:]
        assert exists(expected_dir) is False

        try:
            for i, info, nextdict in multiple_progress_storing_tempdir(tempfolder, iterators, keys):
                if 'iso3' in nextdict and nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        for result in expected_results:
            result[1]['batch'] = start_batch
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'RESET')
        results = list()
        for result in multiple_progress_storing_tempdir(tempfolder, iterators, keys, '1234'):
            results.append(copy.deepcopy(result))
        for result in expected_results:
            result[1]['batch'] = '1234'
        assert results == expected_results
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')

        try:
            for i, info, nextdict in multiple_progress_storing_tempdir(tempfolder, iterators, keys):
                if 'iso3' in nextdict and nextdict['iso3'] == 'YEM':
                    start_batch = info['batch']
                    raise ValueError('Problem!')
        except:
            pass
        for result in expected_results:
            result[1]['batch'] = start_batch
        assert exists(expected_dir) is True
        monkeypatch.setenv('WHERETOSTART', 'iso3=SDN')
        result = list()
        for i, info, nextdict in multiple_progress_storing_tempdir(tempfolder, iterators, keys):
            assert exists(info['folder']) is True
            assert info['folder'] == join(expected_dir, '1')
            assert info['batch'] == start_batch
            result.append(nextdict)
        assert result == iterator2[1:]
        assert exists(expected_dir) is False
        monkeypatch.delenv('WHERETOSTART')
        results = list()

        rmtree(expected_dir, ignore_errors=True)
