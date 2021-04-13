# -*- coding: UTF-8 -*-
"""Retriever Tests"""
import copy
import random
import re
import string
from collections import OrderedDict
from os import remove, mkdir
from os.path import join, abspath
from shutil import rmtree

import pytest

from hdx.utilities.downloader import Download, DownloadError
from hdx.utilities.retriever import Retrieve
from hdx.utilities.useragent import UserAgent


class TestRetriever:
    retrieverfoldername = 'retriever'

    @pytest.fixture(scope='class', autouse=True)
    def useragent(self):
        UserAgent.set_global('test')
        yield
        UserAgent.clear_global()

    @pytest.fixture(scope='class')
    def retrieverfolder(self, fixturesfolder):
        return join(fixturesfolder, self.retrieverfoldername)

    @pytest.fixture(scope='class')
    def fallback_dir(self, retrieverfolder):
        return join(retrieverfolder, 'fallbacks')

    def test_retrieve_file(self, tmpdir, retrieverfolder, fallback_dir):
        tmpdir = str(tmpdir)
        saved_dir = join(tmpdir, 'saved')
        temp_dir = join(tmpdir, 'temp')
        rmtree(temp_dir, ignore_errors=True)
        mkdir(temp_dir)
        with Download() as downloader:
            with pytest.raises(ValueError):
                Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=True, use_saved=True)

            retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=False, use_saved=False)
            filename = 'test.txt'
            url = join(retrieverfolder, filename)
            path = retriever.retrieve_file(url, filename, logstr='test file', fallback=True)
            assert path == join(temp_dir, filename)
            path = retriever.retrieve_file('NOTEXIST', filename, logstr='test file', fallback=True)
            assert path == join(fallback_dir, filename)
            with pytest.raises(DownloadError):
                retriever.retrieve_file('NOTEXIST', filename, fallback=False)
            with pytest.raises(DownloadError):
                long_url = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(150))
                retriever.retrieve_file(long_url, filename, fallback=False)
            text = retriever.retrieve_text(url, filename, logstr='test file', fallback=False)
            assert text == 'hello'
            text = retriever.retrieve_text('NOTEXIST', filename, logstr='test file', fallback=True)
            assert text == 'goodbye'
            with pytest.raises(DownloadError):
                retriever.retrieve_text('NOTEXIST', filename, fallback=False)
            filename = 'test.yaml'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_yaml(url, filename, logstr='test file', fallback=False)
            assert data['param_1'] == 'ABC'
            data = retriever.retrieve_yaml('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['param_1'] == 'XYZ'
            with pytest.raises(DownloadError):
                retriever.retrieve_yaml('NOTEXIST', filename, fallback=False)
            filename = 'test.json'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_json(url, filename, logstr='test file', fallback=False)
            assert data['my_param'] == 'abc'
            data = retriever.retrieve_json('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['my_param'] == 'xyz'
            with pytest.raises(DownloadError):
                retriever.retrieve_json('NOTEXIST', filename, fallback=False)

            retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=True, use_saved=False)
            filename = 'test.txt'
            url = join(retrieverfolder, filename)
            path = retriever.retrieve_file(url, filename, logstr='test file', fallback=True)
            assert path == join(saved_dir, filename)
            path = retriever.retrieve_file('NOTEXIST', filename, logstr='test file', fallback=True)
            assert path == join(fallback_dir, filename)
            with pytest.raises(DownloadError):
                retriever.retrieve_file('NOTEXIST', filename, fallback=False)
            text = retriever.retrieve_text(url, filename, logstr='test file', fallback=False)
            assert text == 'hello'
            text = retriever.retrieve_text('NOTEXIST', filename, logstr='test file', fallback=True)
            assert text == 'goodbye'
            with pytest.raises(DownloadError):
                retriever.retrieve_text('NOTEXIST', filename, fallback=False)
            filename = 'test.yaml'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_yaml(url, filename, logstr='test file', fallback=False)
            assert data['param_1'] == 'ABC'
            data = retriever.retrieve_yaml('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['param_1'] == 'XYZ'
            with pytest.raises(DownloadError):
                retriever.retrieve_yaml('NOTEXIST', filename, fallback=False)
            filename = 'test.json'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_json(url, filename, logstr='test file', fallback=False)
            assert data['my_param'] == 'abc'
            data = retriever.retrieve_json('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['my_param'] == 'xyz'
            with pytest.raises(DownloadError):
                retriever.retrieve_json('NOTEXIST', filename, fallback=False)

            retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=False, use_saved=True)
            filename = 'test.txt'
            url = join(retrieverfolder, filename)
            path = retriever.retrieve_file(url, filename, logstr='test file', fallback=True)
            assert path == join(saved_dir, filename)
            path = retriever.retrieve_file('NOTEXIST', filename, logstr='test file', fallback=True)
            assert path == join(saved_dir, filename)
            path = retriever.retrieve_file('NOTEXIST', filename, fallback=False)
            assert path == join(saved_dir, filename)
            text = retriever.retrieve_text(url, filename, logstr='test file', fallback=False)
            assert text == 'hello'
            text = retriever.retrieve_text('NOTEXIST', filename, logstr='test file', fallback=True)
            assert text == 'hello'
            text = retriever.retrieve_text('NOTEXIST', filename, fallback=False)
            assert text == 'hello'
            filename = 'test.yaml'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_yaml(url, filename, logstr='test file', fallback=False)
            assert data['param_1'] == 'ABC'
            data = retriever.retrieve_yaml('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['param_1'] == 'ABC'
            data = retriever.retrieve_yaml('NOTEXIST', filename, fallback=False)
            assert data['param_1'] == 'ABC'
            filename = 'test.json'
            url = join(retrieverfolder, filename)
            data = retriever.retrieve_json(url, filename, logstr='test file', fallback=False)
            assert data['my_param'] == 'abc'
            data = retriever.retrieve_json('NOTEXIST', filename, logstr='test file', fallback=True)
            assert data['my_param'] == 'abc'
            data = retriever.retrieve_json('NOTEXIST', filename, fallback=False)
            assert data['my_param'] == 'abc'

            retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=False, use_saved=True)
