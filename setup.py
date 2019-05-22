# -*- coding: utf-8 -*-
import sys
from os.path import join

from setuptools import setup, find_packages

sys.path.append('src')  # Only needed for this project
from hdx.utilities import CleanCommand, PackageCommand, PublishCommand
from hdx.utilities.loader import load_file_to_str

requirements = ['basicauth',
                'beautifulsoup4',
                'colorlog',
                'email_validator',
                'html5lib',
                'psycopg2-binary',
                'pyaml',
                'six>=1.12.0',
                'sshtunnel',
                'tabulator>=1.20.0',
                'typing',
                'yamlloader'
                ]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='hdx-python-utilities',
    description='HDX Python Utilities',
    license='MIT',
    url='https://github.com/OCHA-DAP/hdx-python-utilities',
    version=load_file_to_str(join('src', 'hdx', 'utilities', 'version.txt'), strip=True),
    author='Michael Rans',
    author_email='rans@email.com',
    keywords=['HDX', 'utilities', 'library', 'country', 'iso 3166'],
    long_description=load_file_to_str('README.rst'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=True,
    classifiers=classifiers,
    install_requires=requirements,
    cmdclass={'clean': CleanCommand, 'package': PackageCommand, 'publish': PublishCommand},
)
