|Build_Status| |Coverage_Status|

The HDX Python Utilities Library provides a range of helpful utilities:

1. Easy downloading of files with support for authentication, streaming and hashing
#. Simple emailing
#. Easy logging setup
#. Dictionary and list utilities
#. Text block matching
#. Path utilities

This library is part of the `Humanitarian Data Exchange`_ (HDX) project. If you have
humanitarian related data, please upload your datasets to HDX.

-  `Usage <#usage>`__
-  `Configuring Logging <#configuring-logging>`__

Usage
-----

The library has detailed API documentation which can be found
here: \ http://ocha-dap.github.io/hdx-python-utilities/. The code for the
library is here: \ https://github.com/ocha-dap/hdx-python-utilities.

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
.. _Humanitarian Data Exchange: https://data.humdata.org/

