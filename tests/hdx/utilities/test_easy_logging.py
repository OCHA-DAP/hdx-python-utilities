# -*- coding: UTF-8 -*-
"""Logging Tests"""
from logging.handlers import SMTPHandler
from os.path import join

import pytest
import six
from logging_tree import tree

from hdx.utilities.easy_logging import setup_logging, LoggingError

if six.PY3:
    FILENOTFOUND_EXCTYPE = FileNotFoundError  # noqa: F821
else:
    FILENOTFOUND_EXCTYPE = IOError


class TestLogging:
    @pytest.fixture(scope='class')
    def logging_config_yaml(self):
        return join('tests', 'fixtures', 'config', 'logging_config.yml')

    @pytest.fixture(scope='class')
    def logging_config_json(self):
        return join('tests', 'fixtures', 'config', 'logging_config.json')

    @pytest.fixture(scope='class')
    def smtp_config_yaml(self):
        return join('tests', 'fixtures', 'config', 'smtp_config.yml')

    @pytest.fixture(scope='class')
    def smtp_config_json(self):
        return join('tests', 'fixtures', 'config', 'smtp_config.json')

    @staticmethod
    def get_root_handlers_names():
        return [x.name for x in tree()[1].handlers]

    @staticmethod
    def get_root_mail_handler_email():
        for handler in tree()[1].handlers:
            if isinstance(handler, SMTPHandler):
                return handler.toaddrs
        return None

    def test_setup_logging(self, logging_config_json, logging_config_yaml, smtp_config_json, smtp_config_yaml):
        with pytest.raises(FILENOTFOUND_EXCTYPE):
            setup_logging(smtp_config_json='NOT_EXIST')

        with pytest.raises(FILENOTFOUND_EXCTYPE):
            setup_logging(logging_config_json='NOT_EXIST', smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(FILENOTFOUND_EXCTYPE):
            setup_logging(logging_config_yaml='NOT_EXIST', smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(logging_config_yaml=logging_config_yaml, smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(logging_config_dict={'la': 'la'}, logging_config_json=logging_config_json,
                          smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(logging_config_dict={'la': 'la'}, logging_config_yaml=logging_config_yaml,
                          smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(logging_config_json=logging_config_json, logging_config_yaml=logging_config_yaml,
                          smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(smtp_config_dict={'la': 'la'}, smtp_config_json=smtp_config_json)

        with pytest.raises(LoggingError):
            setup_logging(smtp_config_dict={'la': 'la'}, smtp_config_yaml=smtp_config_yaml)

        with pytest.raises(LoggingError):
            setup_logging(smtp_config_json=smtp_config_json, smtp_config_yaml=smtp_config_yaml)

    def test_setup_logging_dict(self, smtp_config_yaml):
        handlers = ['error_file_handler', 'error_mail_handler']
        logging_config_dict = {'version': 1,
                               'handlers': {
                                   'error_file_handler': {
                                       'class': 'logging.FileHandler',
                                       'level': 'ERROR',
                                       'filename': 'errors.log',
                                       'encoding': 'utf8',
                                       'mode': 'w'
                                   },
                                   'error_mail_handler': {
                                       'class': 'logging.handlers.SMTPHandler',
                                       'level': 'CRITICAL',
                                       'mailhost': 'localhost',
                                       'fromaddr': 'noreply@localhost',
                                       'toaddrs': 'abc@abc.com',
                                       'subject': 'SCRAPER FAILED'
                                   }
                               },
                               'root': {
                                   'level': 'INFO',
                                   'handlers': handlers
                               }}
        setup_logging(logging_config_dict=logging_config_dict)
        actual_handler_names = self.get_root_handlers_names()
        for handler in handlers:
            assert handler in actual_handler_names
        assert 'abc@abc.com' in self.get_root_mail_handler_email()

    def test_setup_logging_json(self, logging_config_json):
        setup_logging(logging_config_json=logging_config_json)
        actual_handler_names = self.get_root_handlers_names()
        for handler in ['console', 'error_file_handler']:
            assert handler in actual_handler_names

    def test_setup_logging_yaml(self, monkeypatch, logging_config_yaml):
        setup_logging(logging_config_yaml=logging_config_yaml)
        actual_handler_names = self.get_root_handlers_names()
        for handler in ['console', 'error_mail_handler']:
            assert handler in actual_handler_names
        assert 'abc@abc.com' in self.get_root_mail_handler_email()

    def test_setup_logging_env(self, monkeypatch, logging_config_yaml):
        monkeypatch.setenv('LOG_FILE_ONLY', 'true')
        setup_logging(logging_config_yaml=logging_config_yaml)
        actual_handler_names = self.get_root_handlers_names()
        assert 'console' not in actual_handler_names
        monkeypatch.setenv('LOG_FILE_ONLY', 'false')
        setup_logging(logging_config_yaml=logging_config_yaml)
        actual_handler_names = self.get_root_handlers_names()
        assert 'console' in actual_handler_names

    def test_setup_logging_smtp_dict(self):
        smtp_config_dict = {'handlers': {'error_mail_handler': {'toaddrs': 'lalala@la.com', 'subject': 'lala'}}}
        setup_logging(smtp_config_dict=smtp_config_dict)
        actual_handler_names = self.get_root_handlers_names()
        for handler in ['console', 'error_file_handler', 'error_mail_handler']:
            assert handler in actual_handler_names
        assert 'lalala@la.com' in self.get_root_mail_handler_email()

    def test_setup_logging_smtp_json(self, smtp_config_json):
        setup_logging(smtp_config_json=smtp_config_json)
        actual_handler_names = self.get_root_handlers_names()
        for handler in ['console', 'error_file_handler', 'error_mail_handler']:
            assert handler in actual_handler_names
        assert '123@123.com' in self.get_root_mail_handler_email()

    def test_setup_logging_smtp_yaml(self, smtp_config_yaml):
        setup_logging(smtp_config_yaml=smtp_config_yaml)
        actual_handler_names = self.get_root_handlers_names()
        for handler in ['console', 'error_file_handler', 'error_mail_handler']:
            assert handler in actual_handler_names
        assert 'abc@abc.com' in self.get_root_mail_handler_email()
