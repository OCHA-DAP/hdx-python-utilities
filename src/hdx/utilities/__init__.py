__version__ = "3.0.4"

# TODO: Remove below after all projects that depend on this one are upgraded to use new TOML structure!
import os
import sys
from distutils import log
from distutils.command.clean import clean
from os.path import exists
from shutil import rmtree

from setuptools import Command

sys.path.append("src")


class CleanCommand(clean):
    """
    Custom implementation of ``clean`` setuptools command."""

    def run(self):  # pragma: no cover
        """After calling the super class implementation, this function removes
        the dist directory if it exists."""
        self.all = True  # --all by default when cleaning
        super().run()
        dir_ = "dist"
        if exists(dir_):
            log.info("removing '%s' (and everything under it)", dir_)
            rmtree(dir_)
        else:
            log.info("'%s' does not exist -- can't clean it", dir_)


class PackageCommand(Command):
    """Package command for setup.py that creates source and wheel packages."""

    description = "Build the packages."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info("Building Source and Wheel (universal) Packages...")
        os.system(
            f"{sys.executable} setup.py clean sdist bdist_wheel --universal"
        )
        sys.exit()


class PublishCommand(Command):
    """Publish command for setup.py that creates git tags and publishes to pypi.
    Requires that twine and git be installed."""

    version = None
    description = "Publish the packages."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info("Uploading the package to PyPI using twine...")
        os.system("twine upload dist/*")

        if PublishCommand.version:
            log.info("Pushing git tags...")
            os.system(f"git tag v{PublishCommand.version}")
            os.system("git push --tags")

        sys.exit()
