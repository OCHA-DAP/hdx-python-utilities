# -*- coding: UTF-8 -*-
"""Path Utility Tests"""
from os.path import join
from tempfile import gettempdir

from hdx.utilities.path import temp_dir


class TestPath:
    def test_tempdir(self, monkeypatch):
        assert temp_dir() == gettempdir()
        mytestdir = join('haha', 'lala')
        monkeypatch.setenv('TEMP_DIR', mytestdir)
        assert temp_dir() == mytestdir
