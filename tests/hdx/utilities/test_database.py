# -*- coding: UTF-8 -*-
"""Database Utility Tests"""
import copy
import os
from collections import namedtuple
from os.path import join

import psycopg2
import pytest
from sshtunnel import SSHTunnelForwarder

from hdx.utilities.database import Database


class TestDatabase:
    connected = False
    started = False
    stopped = False
    dbpath = join('tests', 'test_database.db')
    params = {'database': 'mydatabase', 'host': 'myserver', 'port': 1234, 'username': 'myuser', 'password': 'mypass',
              'driver': 'postgres'}
    sqlalchemy_url = 'postgres://myuser:mypass@myserver:1234/mydatabase'

    @pytest.fixture(scope='function')
    def nodatabase(self):
        try:
            os.remove(TestDatabase.dbpath)
        except OSError:
            pass
        return 'sqlite:///%s' % TestDatabase.dbpath

    @pytest.fixture(scope='function')
    def mock_psycopg2(self, monkeypatch):
        def connect(**kwargs):
            if TestDatabase.connected:
                class Connection:
                    @staticmethod
                    def close():
                        return

                return Connection()
            else:
                TestDatabase.connected = True
                raise psycopg2.OperationalError

        monkeypatch.setattr(psycopg2, 'connect', connect)

    @pytest.fixture(scope='function')
    def mock_SSHTunnelForwarder(self, monkeypatch):
        def init(*args, **kwargs):
            return None

        def start(_):
            TestDatabase.started = True

        def stop(_):
            TestDatabase.stopped = True

        monkeypatch.setattr(SSHTunnelForwarder, '__init__', init)
        monkeypatch.setattr(SSHTunnelForwarder, 'start', start)
        monkeypatch.setattr(SSHTunnelForwarder, 'stop', stop)
        monkeypatch.setattr(SSHTunnelForwarder, 'local_bind_port', 5678)

        def get_session(_, db_url):
            class Session:
                bind = namedtuple('Bind', 'engine')

                def close(self):
                    return None

            Session.bind.engine = namedtuple('Engine', 'url')
            Session.bind.engine.url = db_url
            return Session()

        monkeypatch.setattr(Database, 'get_session', get_session)

    def test_get_params_from_sqlalchemy_url(self):
        result = Database.get_params_from_sqlalchemy_url(TestDatabase.sqlalchemy_url)
        assert result == TestDatabase.params

    def test_get_sqlalchemy_url(self):
        result = Database.get_sqlalchemy_url(**TestDatabase.params)
        assert result == TestDatabase.sqlalchemy_url

    def test_wait_for_postgres(self, mock_psycopg2):
        TestDatabase.connected = False
        Database.wait_for_postgres('mydatabase', 'myserver', 5432, 'myuser', 'mypass')
        assert TestDatabase.connected is True

    def test_get_session(self, nodatabase):
        with Database(database=TestDatabase.dbpath, port=None, driver='sqlite') as dbsession:
            assert str(dbsession.bind.engine.url) == nodatabase

    def test_get_session_ssh(self, mock_psycopg2, mock_SSHTunnelForwarder):
        with Database(ssh_host='mysshhost', **TestDatabase.params) as dbsession:
            assert str(dbsession.bind.engine.url) == 'postgres://myuser:mypass@mysshhost:5678/mydatabase'
        params = copy.deepcopy(TestDatabase.params)
        del params['password']
        with Database(ssh_host='mysshhost', ssh_port=25, **params) as dbsession:
            assert str(dbsession.bind.engine.url) == 'postgres://myuser@mysshhost:5678/mydatabase'
