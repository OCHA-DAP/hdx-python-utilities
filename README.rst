|Build_Status| |Coverage_Status|

The HDX Python Utilities Library provides a range of helpful utilities:

1. `Easy downloading of files with support for authentication, streaming and hashing <#downloading-files>`__
#. `Loading and saving JSON and YAML (inc. with OrderedDict) <#loading-and-saving-json-and-yaml>`__
#. `Database utilities (inc. connecting through SSH and SQLAlchemy helpers) <#database-utilities>`__
#. `Dictionary and list utilities <#dictionary-and-list-utilities>`__
#. `HTML utilities (inc. BeautifulSoup helper) <#html-utilities>`__
#. `Compare files (eg. for testing) <#compare-files>`__
#. `Simple emailing <#emailing>`__
#. `Easy logging setup <#configuring-logging>`__
#. `Path utilities <#path-utilities>`__
#. `Text processing <#text-processing>`__
#. `Py3-like raise from for Py2 <#raise-from>`__
#. `Check valid UUID <#valid-uuid>`__


This library is part of the `Humanitarian Data Exchange`_ (HDX) project. If you have
humanitarian related data, please upload your datasets to HDX.

Usage
-----

The library has detailed API documentation which can be found
here: \ http://ocha-dap.github.io/hdx-python-utilities/. The code for the
library is here: \ https://github.com/ocha-dap/hdx-python-utilities.

Downloading files
~~~~~~~~~~~~~~~~~

Various utilities to help with downloading files. Includes retrying by default.

For example, given YAML file extraparams.yml:
::

    mykey:
        basic_auth: "XXXXXXXX"
        locale: "en"

We can create a downloader as shown below that will use the authentication defined
in basic_auth and add the parameter locale=en to each request
(eg. for get request http://myurl/lala?param1=p1&locale=en):
::

    with Download(user_agent='test', extra_params_yaml='extraparams.yml', extra_params_lookup='mykey') as downloader:
        response = downloader.download(url)  # get requests library response
        json = response.json()

        # Download file to folder/filename
        f = downloader.download_file('http://myurl', post=False,
                                     parameters=OrderedDict([('b', '4'), ('d', '3')]),
                                     folder=tmpdir, filename=filename)
        filepath = abspath(f)

        # Read row by row from tabular file
        for row in downloader.get_tabular_rows('http://myurl/my.csv', dict_rows=True, headers=1)
            a = row['col']

If we want a user agent that will be used in all relevant HDX Python Utilities
methods (and all HDX Python API ones too if that library is included), then it
can be configured once and used automatically:
::

    UserAgent.set_global('test')
    with Download() as downloader:
        response = downloader.download(url)  # get requests library response

Other useful functions:

::

    # Build get url from url and dictionary of parameters
    Download.get_url_for_get('http://www.lala.com/hdfa?a=3&b=4',
                             OrderedDict([('c', 'e'), ('d', 'f')]))
        # == 'http://www.lala.com/hdfa?a=3&b=4&c=e&d=f'

    # Extract url and dictionary of parameters from get url
    Download.get_url_params_for_post('http://www.lala.com/hdfa?a=3&b=4',
                                     OrderedDict([('c', 'e'), ('d', 'f')]))
        # == ('http://www.lala.com/hdfa',
              OrderedDict([('a', '3'), ('b', '4'), ('c', 'e'), ('d', 'f')]))

Loading and Saving JSON and YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples:
::

    # Load YAML
    mydict = load_yaml('my_yaml.yml')

    # Load 2 YAMLs and merge into dictionary
    mydict = load_and_merge_yaml('my_yaml1.yml', 'my_yaml2.yml')

    # Load YAML into existing dictionary
    mydict = load_yaml_into_existing_dict(existing_dict, 'my_yaml.yml')

    # Load JSON
    mydict = load_json('my_json.yml')

    # Load 2 JSONs and merge into dictionary
    mydict = load_and_merge_json('my_json1.json', 'my_json2.json')

    # Load JSON into existing dictionary
    mydict = load_json_into_existing_dict(existing_dict, 'my_json.json')

    # Save dictionary to YAML file in pretty format
    # preserving order if it is an OrderedDict
    save_yaml(mydict, 'mypath.yml', pretty=True, sortkeys=False)

    # Save dictionary to JSON file in compact form
    # sorting the keys
    save_json(mydict, 'mypath.json', pretty=False, sortkeys=False)


Database utilities
~~~~~~~~~~~~~~~~~~

These are built on top of SQLAlchemy and simplify its setup.

Your SQLAlchemy database tables must inherit from Base in
hdx.utilities.database eg.
::

    from hdx.utilities.database import Base
    class MyTable(Base):
        my_col = Column(Integer, ForeignKey(MyTable2.col2), primary_key=True)


Examples:
::

    # Get SQLAlchemy session object given database parameters and
    # if needed SSH parameters. If database is PostgreSQL, will poll
    # till it is up.
    with Database(database='db', host='1.2.3.4', username='user', password='pass',
                  driver='driver', ssh_host='5.6.7.8', ssh_port=2222,
                  ssh_username='sshuser', ssh_private_key='path_to_key') as session:
        session.query(...)

    # Extract dictionary of parameters from SQLAlchemy url
    result = Database.get_params_from_sqlalchemy_url(TestDatabase.sqlalchemy_url)

    # Build SQLAlchemy url from dictionary of parameters
    result = Database.get_sqlalchemy_url(**TestDatabase.params)

    # Wait util PostgreSQL is up
    Database.wait_for_postgres('mydatabase', 'myserver', 5432, 'myuser', 'mypass')

Dictionary and list utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples:
::

    # Merge dictionaries
    d1 = {1: 1, 2: 2, 3: 3, 4: ['a', 'b', 'c']}
    d2 = {2: 6, 5: 8, 6: 9, 4: ['d', 'e']}
    result = merge_dictionaries([d1, d2])
    assert result == {1: 1, 2: 6, 3: 3, 4: ['d', 'e'], 5: 8, 6: 9}

    # Diff dictionaries
    d1 = {1: 1, 2: 2, 3: 3, 4: {'a': 1, 'b': 'c'}}
    d2 = {4: {'a': 1, 'b': 'c'}, 2: 2, 3: 3, 1: 1}
    diff = dict_diff(d1, d2)
    assert diff == {}
    d2[3] = 4
    diff = dict_diff(d1, d2)
    assert diff == {3: (3, 4)}

    # Add element to list in dict
    d = dict()
    dict_of_lists_add(d, 'a', 1)
    assert d == {'a': [1]}
    dict_of_lists_add(d, 2, 'b')
    assert d == {'a': [1], 2: ['b']}
    dict_of_lists_add(d, 'a', 2)
    assert d == {'a': [1, 2], 2: ['b']}

    # Spread items in list so similar items are further apart
    input_list = [3, 1, 1, 1, 2, 2]
    result = list_distribute_contents(input_list)
    assert result == [1, 2, 1, 2, 1, 3]

    # Get values for the same key in all dicts in list
    input_list = [{'key': 'd', 1: 5}, {'key': 'd', 1: 1}, {'key': 'g', 1: 2},
                  {'key': 'a', 1: 2}, {'key': 'a', 1: 3}, {'key': 'b', 1: 5}]
    result = extract_list_from_list_of_dict(input_list, 'key')
    assert result == ['d', 'd', 'g', 'a', 'a', 'b']

    # Cast either keys or values or both in dictionary to type
    d1 = {1: 2, 2: 2.0, 3: 5, 'la': 4}
    assert key_value_convert(d1, keyfn=int) == {1: 2, 2: 2.0, 3: 5, 'la': 4}
    assert key_value_convert(d1, keyfn=int, dropfailedkeys=True) == {1: 2, 2: 2.0, 3: 5}
    d1 = {1: 2, 2: 2.0, 3: 5, 4: 'la'}
    assert key_value_convert(d1, valuefn=int) == {1: 2, 2: 2.0, 3: 5, 4: 'la'}
    assert key_value_convert(d1, valuefn=int, dropfailedvalues=True) == {1: 2, 2: 2.0, 3: 5}

    # Cast keys in dictionary to integer
    d1 = {1: 1, 2: 1.5, 3.5: 3, '4': 4}
    assert integer_key_convert(d1) == {1: 1, 2: 1.5, 3: 3, 4: 4}

    # Cast values in dictionary to integer
    d1 = {1: 1, 2: 1.5, 3: '3', 4: 4}
    assert integer_value_convert(d1) == {1: 1, 2: 1, 3: 3, 4: 4}

    # Cast values in dictionary to float
    d1 = {1: 1, 2: 1.5, 3: '3', 4: 4}
    assert float_value_convert(d1) == {1: 1.0, 2: 1.5, 3: 3.0, 4: 4.0}

    # Average values by key in two dictionaries
    d1 = {1: 1, 2: 1.0, 3: 3, 4: 4}
    d2 = {1: 2, 2: 2.0, 3: 5, 4: 4, 7: 3}
    assert avg_dicts(d1, d2) == {1: 1.5, 2: 1.5, 3: 4, 4: 4}

    # Read and write lists to csv
    l = [[1, 2, 3, 'a'],
         [4, 5, 6, 'b'],
         [7, 8, 9, 'c']]
    write_list_to_csv(l, filepath, headers=['h1', 'h2', 'h3', 'h4'])
    newll = read_list_from_csv(filepath)
    newld = read_list_from_csv(filepath, dict_form=True, headers=1)
    assert newll == [['h1', 'h2', 'h3', 'h4'], ['1', '2', '3', 'a'], ['4', '5', '6', 'b'], ['7', '8', '9', 'c']]
    assert newld == [{'h1': '1', 'h2': '2', 'h4': 'a', 'h3': '3'},
                    {'h1': '4', 'h2': '5', 'h4': 'b', 'h3': '6'},
                    {'h1': '7', 'h2': '8', 'h4': 'c', 'h3': '9'}]

    # Convert command line arguments to dictionary
    args = 'a=1,big=hello,1=3'
    assert args_to_dict(args) == {'a': '1', 'big': 'hello', '1': '3'}

HTML utilities
~~~~~~~~~~~~~~

These are built on top of BeautifulSoup and simplify its setup.

Examples:

::

    # Get soup for url with optional kwarg downloader=Download() object
    soup = get_soup('http://myurl', user_agent='test')
    # user agent can be set globally using:
    # UserAgent.set_global('test')
    tag = soup.find(id='mytag')

    # Get text of tag stripped of leading and trailing whitespace
    # and newlines and with &nbsp replaced with space
    result = get_text('mytag')

    # Extract HTML table as list of dictionaries
    result = extract_table(tabletag)

Compare files
~~~~~~~~~~~~~

Compare two files:
::

    result = compare_files(testfile1, testfile2)
    # Result is of form eg.:
    # ["- coal   ,3      ,7.4    ,'needed'\n", '?         ^\n',
    #  "+ coal   ,1      ,7.4    ,'notneeded'\n", '?         ^                +++\n']

Emailing
~~~~~~~~

Example of setup and sending email:
::

    smtp_initargs = {
        'host': 'localhost',
        'port': 123,
        'local_hostname': 'mycomputer.fqdn.com',
        'timeout': 3,
        'source_address': ('machine', 456),
    }
    username = 'user@user.com'
    password = 'pass'
    email_config_dict = {
        'connection_type': 'ssl',
        'username': username,
        'password': password
    }
    email_config_dict.update(smtp_initargs)

    recipients = ['larry@gmail.com', 'moe@gmail.com', 'curly@gmail.com']
    subject = 'hello'
    text_body = 'hello there'
    html_body = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           How are you?<br>
           Here is the <a href="https://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """
    sender = 'me@gmail.com'

    with Email(email_config_dict=email_config_dict) as email:
        email.send(recipients, subject, text_body, sender=sender)

Configuring Logging
~~~~~~~~~~~~~~~~~~~

The library provides coloured logs with a simple default setup which
should be adequate for most cases. If you wish to change the logging
configuration from the defaults, you will need to call 
\ **setup_logging** with arguments.

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

Path utilities
~~~~~~~~~~~~~~

Examples:
::

    # Gets temporary directory from environment variable
    # TEMP_DIR and falls back to os function
    temp_folder = get_temp_dir()

    # Gets temporary directory from environment variable
    # TEMP_DIR and falls back to os function,
    # optionally appends the given folder, creates the
    # folder and on exiting, deletes the folder
    with temp_dir('papa') as tempdir:
        ...

    # Get current directory of script
    dir = script_dir(ANY_PYTHON_OBJECT_IN_SCRIPT)

    # Get current directory of script with filename appended
    path = script_dir_plus_file('myfile.txt', ANY_PYTHON_OBJECT_IN_SCRIPT)


Text processing
~~~~~~~~~~~~~~~

Examples:
::

    # Replace multiple strings in a string simultaneously
    a = 'The quick brown fox jumped over the lazy dog. It was so fast!'
    result = multiple_replace(a, {'quick': 'slow', 'fast': 'slow', 'lazy': 'busy'})
    assert result == 'The slow brown fox jumped over the busy dog. It was so slow!'

    # Extract words from a string sentence into a list
    result = get_words_in_sentence("Korea (Democratic People's Republic of)")
    assert result == ['Korea', 'Democratic', "People's", 'Republic', 'of']

    # Find matching text in strings
    a = 'The quick brown fox jumped over the lazy dog. It was so fast!'
    b = 'The quicker brown fox leapt over the slower fox. It was so fast!'
    c = 'The quick brown fox climbed over the lazy dog. It was so fast!'
    result = get_matching_text([a, b, c], match_min_size=10)
    assert result == ' brown fox  over the  It was so fast!'


Raise from
~~~~~~~~~~

Examples:
::

    # Raise an exception from another exception on Py2 or Py3
    except IOError as e:
        raisefrom(IOError, 'My Error Message', e)


Valid UUID
~~~~~~~~~~

Examples:
::

    assert is_valid_uuid('jpsmith') is False
    assert is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a') is True


.. |Build_Status| image:: https://travis-ci.org/OCHA-DAP/hdx-python-utilities.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/OCHA-DAP/hdx-python-utilities
.. |Coverage_Status| image:: https://coveralls.io/repos/github/OCHA-DAP/hdx-python-utilities/badge.svg?branch=master
    :alt: Coveralls Build Status
    :target: https://coveralls.io/github/OCHA-DAP/hdx-python-utilities?branch=master
.. _Humanitarian Data Exchange: https://data.humdata.org/

