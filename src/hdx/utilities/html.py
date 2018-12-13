# -*- coding: utf-8 -*-
"""HTML parsing utilities"""

import logging
from typing import List, Dict, Optional, Any

from bs4 import BeautifulSoup, Tag

from hdx.utilities.downloader import Download

logger = logging.getLogger(__name__)


def get_soup(url, downloader=None, user_agent=None, user_agent_config_yaml=None, user_agent_lookup=None, **kwargs):
    # type: (str, Download, Optional[str], Optional[str], Optional[str], Any) -> BeautifulSoup
    """
    Get BeautifulSoup object for a url. Requires either global user agent to be set or appropriate user agent
    parameter(s) to be completed.

    Args:
        url (str): url to read
        downloader (Download): Download object. Defaults to creating a Download object with given user agent values.
        user_agent (Optional[str]): User agent string. HDXPythonUtilities/X.X.X- is prefixed.
        user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
        user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.

    Returns:
        BeautifulSoup: The BeautifulSoup object for a url

    """
    if not downloader:
        downloader = Download(user_agent, user_agent_config_yaml, user_agent_lookup, **kwargs)
    response = downloader.download(url)
    return BeautifulSoup(response.text, 'html.parser')


def get_text(tag):
    # type: (Tag) -> str
    """
    Get text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

    Args:
        tag (Tag): BeautifulSoup tag

    Returns:
        str: Text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

    """
    return tag.get_text().strip(' \t\n\r').replace(u'\xa0', u' ')


def extract_table(tabletag):
    # type: (Tag) -> List[Dict]
    """
    Extract HTML table as list of dictionaries

    Args:
        tabletag (Tag): BeautifulSoup tag

    Returns:
        str: Text of tag stripped of leading and trailing whitespace and newlines and with &nbsp replaced with space

    """
    theadtag = tabletag.find_next('thead')

    headertags = theadtag.find_all('th')
    if len(headertags) == 0:
        headertags = theadtag.find_all('td')
    headers = []
    for tag in headertags:
        headers.append(get_text(tag))

    tbodytag = tabletag.find_next('tbody')
    trtags = tbodytag.find_all('tr')

    table = list()
    for trtag in trtags:
        row = dict()
        tdtags = trtag.find_all('td')
        for i, tag in enumerate(tdtags):
            row[headers[i]] = get_text(tag)
        table.append(row)
    return table

