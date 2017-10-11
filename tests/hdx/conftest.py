# -*- coding: UTF-8 -*-
"""Global fixtures"""
import smtplib
from os.path import join

import pytest


@pytest.fixture(scope='session')
def fixturesfolder():
    return join('tests', 'fixtures')


@pytest.fixture(scope='session')
def configfolder(fixturesfolder):
        return join(fixturesfolder, 'config')


@pytest.fixture(scope='function')
def mocksmtp(monkeypatch):
    class MockSMTPBase(object):
        type = None

        def __init__(self, **kwargs):
            self.initargs = kwargs

        def login(self, username, password):
            self.username = username
            self.password = password

        def sendmail(self, sender, recipients, msg, **kwargs):
            self.sender = sender
            self.recipients = recipients
            self.msg = msg
            self.send_args = kwargs

        @staticmethod
        def quit():
            pass

    class MockSMTPSSL(MockSMTPBase):
        type = 'smtpssl'

    class MockLMTP(MockSMTPBase):
        type = 'lmtp'

    class MockSMTP(MockSMTPBase):
        type = 'smtp'
    monkeypatch.setattr(smtplib, 'SMTP_SSL', MockSMTPSSL)
    monkeypatch.setattr(smtplib, 'LMTP', MockLMTP)
    monkeypatch.setattr(smtplib, 'SMTP', MockSMTP)
