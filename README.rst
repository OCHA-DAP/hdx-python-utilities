|Build_Status| |Coverage_Status|

The HDX Python Utilities Library provides a range of helpful utilities:

1. Country mappings including ISO 2/3 letter (ISO 3166) and region (uses World Bank live api with static file fallback)
#. Easy downloading of files with support for authentication, streaming and hashing
#. Simple emailing
#. Easy logging setup
#. Dictionary and list utilities
#. Text block matching
#. Path utilities

-  `Usage <#usage>`__
-  `Countries <#countries>`__
-  `Configuring Logging <#configuring-logging>`__

Usage
-----

The library has detailed API documentation which can be found
here: \ http://ocha-dap.github.io/hdx-python-utilities/. The code for the
library is here: \ https://github.com/ocha-dap/hdx-python-utilities.

Countries
~~~~~~~~~

The usage of the country mappings functionality is best illustrated by some examples:

::

    from hdx.utilities.location import Location
    location = Location()

    location.get_country_name_from_iso3('jpn')  # returns 'Japan'
    location.get_country_name_from_iso2('Pl')  # returns 'Poland'
    location.get_iso3_country_code('UZBEKISTAN')  # returns 'UZB'

    location.get_iso3_country_code_partial('Sierra')
    # performs partial match and returns ('SLE', False)

    location.get_country_info_from_iso2('jp')
    # {'id': 'JPN', 'iso2Code': 'JP', 'name': 'Japan',
    # 'latitude': '35.67', 'longitude': '139.77',
    # 'region': {'value': 'East Asia & Pacific', 'id': 'EAS'},
    # 'adminregion': {'value': '', 'id': ''}, 'capitalCity': 'Tokyo',
    # 'incomeLevel': {'value': 'High income', 'id': 'HIC'},
    # 'lendingType': {'value': 'Not classified', 'id': 'LNX'}}

    location.get_countries_in_region('South Asia')
    # ['AFG', 'BGD', 'BTN', 'IND', 'LKA', 'MDV', 'NPL', 'PAK']

Configuring Logging
~~~~~~~~~~~~~~~~~~~

The library provides coloured logs with a simple default setup. If you wish
to change the logging configuration from the defaults, you will need to
call \ **setup_logging** with arguments.

::

    from hdx.utilities.easy_logging import setup_logging
    ...
    logger = logging.getLogger(__name__)
    setup_logging(KEYWORD ARGUMENTS)

**KEYWORD ARGUMENTS** can be:

+-----------+-----------------------+------+--------------------------+----------------------------+
| Choose    | Argument              | Type | Value                    | Default                    |
|           |                       |      |                          |                            |
+===========+=======================+======+==========================+============================+
| One of:   | logging\_config\_dict | dict | Logging configuration    |                            |
|           |                       |      | dictionary               |                            |
+-----------+-----------------------+------+--------------------------+----------------------------+
| or        | logging\_config\_json | str  | Path to JSON Logging     |                            |
|           |                       |      | configuration            |                            |
+-----------+-----------------------+------+--------------------------+----------------------------+
| or        | logging\_config\_yaml | str  | Path to YAML Logging     | Library's internal         |
|           |                       |      | configuration            | logging\_configuration.yml |
+-----------+-----------------------+------+--------------------------+----------------------------+
| One of:   | smtp\_config\_dict    | dict | Email Logging            |                            |
|           |                       |      | configuration dictionary |                            |
+-----------+-----------------------+------+--------------------------+----------------------------+
| or        | smtp\_config\_json    | str  | Path to JSON Email       |                            |
|           |                       |      | Logging configuration    |                            |
+-----------+-----------------------+------+--------------------------+----------------------------+
| or        | smtp\_config\_yaml    | str  | Path to YAML Email       |                            |
|           |                       |      | Logging configuration    |                            |
+-----------+-----------------------+------+--------------------------+----------------------------+

Do not supply **smtp_config_dict**, **smtp_config_json** or
**smtp_config_yaml** unless you are using the default logging
configuration!

If you are using the default logging configuration, you have the option
to have a default SMTP handler that sends an email in the event of a
CRITICAL error by supplying either **smtp_config_dict**,
**smtp_config_json** or **smtp_config_yaml**. Here is a template of a
YAML file that can be passed as the **smtp_config_yaml** parameter:

::

    handlers:
        error_mail_handler:
            toaddrs: EMAIL_ADDRESSES
            subject: "RUN FAILED: MY_PROJECT_NAME"

Unless you override it, the mail server **mailhost** for the default
SMTP handler is **localhost** and the from address **fromaddr** is
**noreply@localhost**.

To use logging in your files, simply add the line below to the top of
each Python file:

::

    logger = logging.getLogger(__name__)

Then use the logger like this:

::

    logger.debug('DEBUG message')
    logger.info('INFORMATION message')
    logger.warning('WARNING message')
    logger.error('ERROR message')
    logger.critical('CRITICAL error message')

.. |Build_Status| image:: https://travis-ci.org/OCHA-DAP/hdx-python-utilities.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/OCHA-DAP/hdx-python-utilities
.. |Coverage_Status| image:: https://coveralls.io/repos/github/OCHA-DAP/hdx-python-utilities/badge.svg?branch=master
    :alt: Coveralls Build Status
    :target: https://coveralls.io/github/OCHA-DAP/hdx-python-utilities?branch=master

