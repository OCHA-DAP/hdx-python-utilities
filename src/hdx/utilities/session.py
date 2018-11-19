# -*- coding: utf-8 -*-
"""Session utilities for urls"""
import logging
import os
from typing import Any

import requests
from basicauth import decode
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from hdx.utilities.loader import load_file_to_str, load_json, load_yaml

logger = logging.getLogger(__name__)


class SessionError(Exception):
    pass


def get_session(**kwargs):
    # type: (Any) -> requests.Session
    """Set up and return Session object that is set up with retrying

    Args:
        **kwargs: See below
        auth (Tuple[str, str]): Authorisation information in tuple form (user, pass) OR
        basic_auth (str): Authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx) OR
        basic_auth_file (str): Path to file containing authorisation information in basic auth string form (Basic xxxxxxxxxxxxxxxx)
        extra_params_dict (Dict): Extra parameters to put on end of url as a dictionary OR
        extra_params_json (str): Path to JSON file containing extra parameters to put on end of url OR
        extra_params_yaml (str): Path to YAML file containing extra parameters to put on end of url
        extra_params_lookup (str): Lookup key for parameters. If not given assumes parameters are at root of the dict.
        status_forcelist (iterable): HTTP statuses for which to force retry. Defaults to [429, 500, 502, 503, 504].
        method_whitelist (iterable): HTTP methods for which to force retry. Defaults t0 frozenset(['GET']).
    """
    s = requests.Session()

    extra_params = os.getenv('EXTRA_PARAMS')
    if extra_params is not None:
        extra_params_dict = dict()
        if '=' in extra_params:
            logger.info('Loading extra parameters from environment variable')
            for extra_param in extra_params.split(','):
                key, value = extra_param.split('=')
                extra_params_dict[key] = value
    else:
        extra_params_found = False
        extra_params_dict = kwargs.get('extra_params_dict')
        if extra_params_dict:
            extra_params_found = True
            logger.info('Loading extra parameters from dictionary')

        extra_params_json = kwargs.get('extra_params_json', '')
        if extra_params_json:
            if extra_params_found:
                raise SessionError('More than one set of extra parameters given!')
            extra_params_found = True
            logger.info('Loading extra parameters from: %s' % extra_params_json)
            extra_params_dict = load_json(extra_params_json)

        extra_params_yaml = kwargs.get('extra_params_yaml', '')
        if extra_params_found:
            if extra_params_yaml:
                raise SessionError('More than one set of extra parameters given!')
        else:
            if extra_params_yaml:
                logger.info('Loading extra parameters from: %s' % extra_params_yaml)
                extra_params_dict = load_yaml(extra_params_yaml)
            else:
                extra_params_dict = dict()
        extra_params_lookup = kwargs.get('extra_params_lookup')
        if extra_params_lookup:
            extra_params_dict = extra_params_dict.get(extra_params_lookup)
            if extra_params_dict is None:
                raise SessionError('%s does not exist in extra_params!' % extra_params_lookup)

    auth_found = False
    basic_auth = os.getenv('BASIC_AUTH')
    if basic_auth:
        logger.info('Loading authorisation from basic_auth environment variable')
        auth_found = True
    else:
        basic_auth = kwargs.get('basic_auth')
        if basic_auth:
            logger.info('Loading authorisation from basic_auth argument')
            auth_found = True
    bauth = extra_params_dict.get('basic_auth')
    if bauth:
        if not auth_found:
            basic_auth = bauth
            logger.info('Loading authorisation from basic_auth parameter')
            auth_found = True
        del extra_params_dict['basic_auth']
    s.params = extra_params_dict

    auth = kwargs.get('auth')
    if auth:
        if auth_found:
            raise SessionError('More than one authorisation given!')
        logger.info('Loading authorisation from auth argument')
        auth_found = True
    basic_auth_file = kwargs.get('basic_auth_file')
    if basic_auth_file:
        if auth_found:
            raise SessionError('More than one authorisation given!')
        logger.info('Loading authorisation from: %s' % basic_auth_file)
        basic_auth = load_file_to_str(basic_auth_file)
    if basic_auth:
        auth = decode(basic_auth)
    s.auth = auth

    status_forcelist = kwargs.get('status_forcelist', [429, 500, 502, 503, 504])
    method_whitelist = kwargs.get('method_whitelist', frozenset(['HEAD', 'TRACE', 'GET', 'PUT', 'OPTIONS', 'DELETE']))

    retries = Retry(total=5, backoff_factor=0.4, status_forcelist=status_forcelist, method_whitelist=method_whitelist,
                    raise_on_redirect=True,
                    raise_on_status=True)
    s.mount('http://', HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100))
    s.mount('https://', HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100))
    return s
