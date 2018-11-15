# -*- coding: utf-8 -*-
"""Database utilities"""
import logging
import time
from typing import Dict, Any, Optional

import psycopg2
from six.moves.urllib.parse import urlsplit
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool
from sshtunnel import SSHTunnelForwarder

logger = logging.getLogger(__name__)


class HDXBase(object):
    @declared_attr
    def __tablename__(cls):
        return '%ss' % cls.__name__.lower()


Base = declarative_base(cls=HDXBase)


class Database(object):
    """Database helper class to handle ssh tunnels, waiting for PostgreSQL to be up etc.

    Args:
        database (Optional[str]): Database name
        host (Optional[str]): Host where database is located
        username (Optional[str]): Username to log into database
        password (Optional[str]): Password to log into database
        port (Optional[int]): Database port. Defaults to 5432.
        driver (str): Database driver. Defaults to 'postgres'.
        **kwargs: See below
        ssh_host (str): SSH host (the server to connect to)
        ssh_port (int): SSH port. Defaults to 22.
        ssh_username (str): SSH username
        ssh_password (str): SSH password
        ssh_private_key: Location of SSH private key (instead of ssh_password)
        For more advanced usage, see SSHTunnelForwarder documentation.

    """

    def __init__(self, database=None, host=None, username=None, password=None, port=5432, driver='postgres', **kwargs):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str], Optional[int], str, Any) -> None
        if len(kwargs) != 0:
            ssh_host = kwargs['ssh_host']
            del kwargs['ssh_host']
            ssh_port = kwargs.get('ssh_port')
            if ssh_port:
                del kwargs['ssh_port']
            else:
                ssh_port = 22
            self.server = SSHTunnelForwarder((host, ssh_port), remote_bind_address=(ssh_host, port), **kwargs)
            self.server.start()
            host = ssh_host
            port = self.server.local_bind_port
        else:
            self.server = None
        if driver == 'postgres':
            Database.wait_for_postgres(database, host, username, password, port)
        db_url = self.get_sqlalchemy_url(database, host, username, password, port=port, driver=driver)
        self.session = self.get_session(db_url)

    def __enter__(self):
        # type: () -> Session
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Any, Any, Any) -> None
        self.session.close()
        if self.server is not None:
            self.server.stop()

    @staticmethod
    def get_session(db_url):
        # type: (str) -> Session
        """Gets PostgreSQL database connection parameters from SQLAlchemy url

        Args:
            db_url (str): SQLAlchemy url

        Returns:
            sqlalchemy.orm.session.Session: SQLAlchemy session
        """
        engine = create_engine(db_url, poolclass=NullPool, echo=False)
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        return Session()

    @staticmethod
    def get_params_from_sqlalchemy_url(db_url):
        # type: (str) -> Dict[str,Any]
        """Gets PostgreSQL database connection parameters from SQLAlchemy url

        Args:
            db_url (str): SQLAlchemy url

        Returns:
            Dict[str,Any]: Dictionary of database connection parameters
        """
        result = urlsplit(db_url)
        return {'host': result.hostname, 'port': result.port, 'username': result.username, 'password': result.password,
                'database': result.path[1:], 'driver': result.scheme}

    @staticmethod
    def get_sqlalchemy_url(database=None, host=None, username=None, password=None, port=5432, driver='postgres'):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str], Optional[int], str) -> str
        """Gets SQLAlchemy url from database connection parameters

        Args:
            database (Optional[str]): Database name
            host (Optional[str]): Host where database is located
            username (Optional[str]): Username to log into database
            password (Optional[str]): Password to log into database
            port (Optional[int]): Database port. Defaults to 5432.
            driver (str): Database driver. Defaults to 'postgres'.

        Returns:
            db_url (str): SQLAlchemy url
        """
        strings = ['%s://' % driver]
        if username:
            strings.append(username)
            if password:
                strings.append(':%s@' % password)
            else:
                strings.append('@')
        if host:
            strings.append(host)
        if port is not None:
            strings.append(':%d' % port)
        if database:
            strings.append('/%s' % database)
        return ''.join(strings)

    @staticmethod
    def wait_for_postgres(database, host, username, password, port=5432):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str], Optional[int]) -> None
        """Waits for PostgreSQL database to be up

        Args:
            database (Optional[str]): Database name
            host (Optional[str]): Host where database is located
            username (Optional[str]): Username to log into database
            password (Optional[str]): Password to log into database
            port (Optional[int]): Database port. Defaults to 5432.

        Returns:
            None
        """
        connecting_string = 'Checking for PostgreSQL...'
        while True:
            try:
                logger.info(connecting_string)
                connection = psycopg2.connect(
                    database=database,
                    user=username,
                    password=password,
                    host=host,
                    port=port,
                    connect_timeout=3
                )
                connection.close()
                logger.info('PostgreSQL is running!')
                break
            except psycopg2.OperationalError:
                time.sleep(1)
