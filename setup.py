import sys
from os.path import join

from setuptools import setup

sys.path.append("src")  # Only needed for this project
from hdx.utilities import (
    CleanCommand,
    PackageCommand,
    PublishCommand,
)
from hdx.utilities.loader import load_file_to_str

PublishCommand.version = load_file_to_str(
    join("src", "hdx", "utilities", "version.txt"), strip=True
)

setup(
    version=PublishCommand.version,
    cmdclass={
        "clean": CleanCommand,
        "package": PackageCommand,
        "publish": PublishCommand,
    },
)
