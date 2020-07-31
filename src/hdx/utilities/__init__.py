import os
import sys
from setuptools import Command
from distutils import log
from distutils.command.clean import clean
from os.path import exists
from shutil import rmtree
from typing import Any
from uuid import UUID, uuid4

import six


def raisefrom(exc_type, message, exc):
    # type: (Any, str, BaseException) -> None
    """Call Python 3 raise from or emulate it for Python 2

    Args:
        exc_type (Any): Type of Exception
        message (str): Error message to display
        exc (BaseException): original exception

    Returns:
        None

    """
    if sys.version_info[:2] >= (3, 2):
        six.raise_from(exc_type(message), exc)
    else:
        six.reraise(exc_type, '%s - %s' % (message, exc), sys.exc_info()[2])


def get_uuid():
    # type: () -> str
    """
    Get an UUID.

    Returns:
        str: A UUID
    """
    return str(uuid4())


def is_valid_uuid(uuid_to_test, version=4):
    # type: (str, int) -> bool
    """
    Check if uuid_to_test is a valid UUID.

    Args:
        uuid_to_test (str): UUID to test for validity
        version (int): UUID version. Defaults to 4.

    Returns:
        str: Current script's directory
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except:
        return False
    return str(uuid_obj) == uuid_to_test


class CleanCommand(clean):
    """
    Custom implementation of ``clean`` setuptools command."""

    def run(self):  # pragma: no cover
        """After calling the super class implementation, this function removes
        the dist directory if it exists."""
        self.all = True  # --all by default when cleaning
        super(CleanCommand, self).run()
        dir_ = 'dist'
        if exists(dir_):
            log.info("removing '%s' (and everything under it)", dir_)
            rmtree(dir_)
        else:
            log.info("'%s' does not exist -- can't clean it", dir_)


class PackageCommand(Command):
    """Package command for setup.py that creates source and wheel packages."""

    description = 'Build the packages.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info('Building Source and Wheel (universal) Packages...')
        os.system('{0} setup.py clean sdist bdist_wheel --universal'.format(sys.executable))
        sys.exit()


class PublishCommand(Command):
    """Publish command for setup.py that creates git tags and publishes to pypi.
    Requires that twine and git be installed."""

    version = None
    description = 'Publish the packages.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info('Uploading the package to PyPI using twine...')
        os.system('twine upload dist/*')

        if PublishCommand.version:
            log.info('Pushing git tags...')
            os.system('git tag v{0}'.format(PublishCommand.version))
            os.system('git push --tags')

        sys.exit()
