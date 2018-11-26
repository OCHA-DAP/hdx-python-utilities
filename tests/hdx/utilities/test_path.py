# -*- coding: UTF-8 -*-
"""Path Utility Tests"""
from os.path import join
from tempfile import gettempdir

from hdx.utilities.path import get_temp_dir, temp_dir


class TestPath:
    def test_tempdir(self, monkeypatch):
        assert get_temp_dir() == gettempdir()
        mytestdir = join('haha', 'lala')
        monkeypatch.setenv('TEMP_DIR', mytestdir)
        assert get_temp_dir() == mytestdir
        with temp_dir() as tempdir:
            assert tempdir == mytestdir
        with temp_dir('papa') as tempdir:
            assert tempdir == join(mytestdir, 'papa')
