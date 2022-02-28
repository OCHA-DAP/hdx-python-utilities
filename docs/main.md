# Summary

The HDX Python Utilities Library provides a range of helpful utilities for Python developers.
Note that these are not specific to HDX.

# Contents

1. [Easy downloading of files with support for authentication, streaming and hashing](#downloading-files)
1. [Retrieval of data from url with saving to file or from data previously saved](#retrieving-files)
1. [Loading and saving JSON and YAML (inc. with OrderedDict)](#loading-and-saving-json-and-yaml)
1. [Dictionary and list utilities](#dictionary-and-list-utilities)
1. [HTML utilities (inc. BeautifulSoup helper)](#html-utilities)
1. [Compare files (eg. for testing)](#comparing-files)
1. [Simple emailing](#emailing)
1. [Easy logging setup and error logging](#logging)
1. [Path utilities](#path-utilities)
1. [Date parsing utilities](#date-parsing-utilities)
1. [Text processing](#text-processing)
1. [Encoding utilities](#encoding-utilities)
1. [Check valid UUID](#valid-uuid)
1. [Easy building and packaging](#easy-building-and-packaging)

# Information

This library is part of the [Humanitarian Data Exchange](https://data.humdata.org/) (HDX) project. If you have 
humanitarian related data, please upload your datasets to HDX.

The code for the library is [here](https://github.com/OCHA-DAP/hdx-python-utilities).
The library has detailed API documentation which can be found in the menu on the left and starts 
[here](https://hdx-python-utilities.readthedocs.io/en/latest/api-documentation/downloading-files/). 

## Breaking Changes

From 3.1.5, changed setup_logging parameters to console_log_level, log_file and 
file_log_level.

From 3.1.1, setup_logging now sets up logaru instead of colorlog and has only one 
parameter error_file which is False by default. There is no longer SMTP (email) handling
which can be done directly with logaru instead.

From 3.0.7, send method of Email class has parameter to rather than recipients. The parameters to, cc and bcc
take either a string email address or list of string email addresses.

From 3.0.3, build stack has changed. Now uses tox, codecov etc. setup.py clean, package and publish removed.
is_valid_uuid and get_uuid are now under hdx.utilities.uuid.

From 3.0.1, removed raisefrom function

From 3.0.0, only supports Python >= 3.6

From 2.6.9, the Download class and get_session have optional allowed_methods instead of optional method_whitelist

From 2.5.5, the Database class and all the libraries on which it depended have been moved to the new 
[HDX Python Database library](https://github.com/OCHA-DAP/hdx-python-database).

From 2.1.2, get_tabular_rows in the Download class returns headers, iterator and a new method get_tabular_rows_as_list 
returns only the iterator.

From 2.1.4, read_list_from_csv and write_list_to_csv change the order of their parameters to be more logical.
Arguments about choosing between dict and list are all made consistent - dict_form.

# Description of Utilities

## Downloading files

Various utilities to help with downloading files. Includes retrying by default.

For example, given YAML file extraparams.yml:

    mykey:
        basic_auth: "XXXXXXXX"
        locale: "en"

We can create a downloader as shown below that will use the authentication defined in basic\_auth and add the parameter 
locale=en to each request (eg. for get request <http://myurl/lala?param1=p1&locale=en>):

    with Download(user_agent="test", extra_params_yaml="extraparams.yml", extra_params_lookup="mykey") as downloader:
        response = downloader.download(url)  # get requests library response
        json = response.json()

        # Download file to folder/filename
        f = downloader.download_file("http://myurl", post=False,
                                     parameters=OrderedDict([("b", "4"), ("d", "3")]),
                                     folder=tmpdir, filename=filename)
        filepath = abspath(f)

        # Read row by row from tabular file
        for row in downloader.get_tabular_rows("http://myurl/my.csv", dict_rows=True, headers=1)
            a = row["col"]

If we want to limit the rate of get and post requests to say 1 per 0.1 seconds, then the rate_limit parameter can be 
passed:

    with Download(rate_limit={"calls": 1, "period": 0.1}) as downloader:
        response = downloader.download(url)  # get requests library response

If we want a user agent that will be used in all relevant HDX Python Utilities methods (and all HDX Python API ones too 
if that library is included), then it can be configured once and used automatically:

    UserAgent.set_global("test")
    with Download() as downloader:
        response = downloader.download(url)  # get requests library response

The response is of the form produced by the requests library. It may not be needed as there are functions directly on 
the Download object eg.

    assert downloader.get_status() == 200
    assert len(downloader.get_headers()) == 24
    assert bool(re.match(r"7\d\d", downloader.get_header("Content-Length"))) is True
    assert downloader.get_text() == "XXX"
    assert downloader.get_json() == {...}
    assert downloader.get_yaml() == {...}

The get_tabular_rows method enables iteration through tabular data. It returns the header of tabular file pointed to by 
the url and an iterator where each row is returned as a list or dictionary depending on the dict_rows argument.

The headers argument is either a row number or list of row numbers (in case of multi-line headers) to be considered as 
headers (rows start counting at 1), or the actual headers defined a list of strings. It defaults to 1 and cannot be 
None. The dict_form arguments specifies if each row should be returned as a dictionary or a list, defaulting to a list.  

Optionally, headers can be inserted at specific positions. This is achieved using the header_insertions argument. If 
supplied, it is a list of tuples of the form (position, header) to be inserted. Optionally a function can be called on 
each row. If supplied, it takes as arguments: headers (prior to any insertions) and row (which will be in dict or list 
form depending upon the dict_rows argument) and outputs a modified row. Example:

    def testfn(headers, row):
        row["la"] = "lala"
        return row

    insertions = {"headers": [(2, "la")], "function": testfn}
    headers, generator = downloader.get_tabular_rows(url, headers=3, 
                                                     header_insertions=[(2, "la")], row_function=testfn)

Other useful functions:

    # Iterate through tabular file returning lists for each row
    for row in downloader.get_tabular_rows_as_list(url):
        ...
    # Get hxl row
    assert Download.hxl_row(["a", "b", "c"], {"b": "#b", "c": "#c"}, dict_form=True)
    # == {"a": "", "b": "#b", "c": "#c"}        
    # Build get url from url and dictionary of parameters
    Download.get_url_for_get("http://www.lala.com/hdfa?a=3&b=4",
                             OrderedDict([("c", "e"), ("d", "f")]))
    # == "http://www.lala.com/hdfa?a=3&b=4&c=e&d=f"

    # Extract url and dictionary of parameters from get url
    Download.get_url_params_for_post("http://www.lala.com/hdfa?a=3&b=4",
                                     OrderedDict([("c", "e"), ("d", "f")]))
    # == ("http://www.lala.com/hdfa",
              OrderedDict([("a", "3"), ("b", "4"), ("c", "e"), ("d", "f")]))
    # Get mapping of columns positions of headers          
    Download.get_column_positions(["a", "b", "c"])
    # == {"a": 0, "b": 1, "c": 2}

For more detail and additional functions, check the API docs mentioned earlier in the [usage section](#usage).

## Retrieving files

When you download a file, you can opt to download from the web as usual or download from the web and and save for future
reuse or use the previously downloaded file. The advantage is this is all handled in the class so you don't need to do 
lots of if-else conditions for the different cases for each download in your code. This is helpful for example when 
trying to generate test data. 

All the downloads in your code can be switched between the different modes by setting the save and use_saved flags when 
constructing the Retrieve object.

    retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save, use_saved)

- save=False, use_saved=False  - download from web as normal (files will go in temp_folder and be discarded)
- save=True, use_saved=False - download from web as normal (files will go in saved_dir and will be kept)
- save=False, use_saved=True - use files from saved_dir (don't download at all)

fallback_dir is a folder containing static fallback files which can optionally be used if the download fails.

Methods in the Retrieve class are: 
- retrieve_file returns a path to a file
- retrieve_text returns the text in a file
- retrieve_json returns the JSON in a Python dict
- retrieve_yaml returns the YAML in a Python dict.

Examples:

    with Download() as downloader:
        # Downloads file returning the path to the downloaded file and using a fallback file if the download 
        # fails. Since saved is False, the file will be saved with name filename in temp_dir
        retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=False, use_saved=False) 
        path = retriever.retrieve_file(url, filename, logstr="my file", fallback=True)

        # Downloads text file saving it for future usage and returning the text data (with no fallback) 
        # Since saved is True, the file will be saved with name filename in saved_dir
        retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=True, use_saved=False)
        text = retriever.retrieve_text(url, filename, logstr="test text", fallback=False)
        # Downloads YAML file saving it for future usage and returning the YAML data with fallback taken
        # from fallback_dir if needed.
        data = retriever.retrieve_yaml(url, filename, logstr="test yaml", fallback=True)

        # Uses previously downloaded JSON file in saved_dir returning the JSON data (with no fallback) 
        retriever = Retrieve(downloader, fallback_dir, saved_dir, temp_dir, save=False, use_saved=True)
        data = retriever.retrieve_json(url, filename, logstr="test json", fallback=False)

## Loading and saving JSON and YAML

Examples:

    # Load YAML
    mydict = load_yaml("my_yaml.yml")

    # Load 2 YAMLs and merge into dictionary
    mydict = load_and_merge_yaml("my_yaml1.yml", "my_yaml2.yml")

    # Load YAML into existing dictionary
    mydict = load_yaml_into_existing_dict(existing_dict, "my_yaml.yml")

    # Load JSON
    mydict = load_json("my_json.yml")

    # Load 2 JSONs and merge into dictionary
    mydict = load_and_merge_json("my_json1.json", "my_json2.json")

    # Load JSON into existing dictionary
    mydict = load_json_into_existing_dict(existing_dict, "my_json.json")

    # Save dictionary to YAML file in pretty format
    # preserving order if it is an OrderedDict
    save_yaml(mydict, "mypath.yml", pretty=True, sortkeys=False)

    # Save dictionary to JSON file in compact form
    # sorting the keys
    save_json(mydict, "mypath.json", pretty=False, sortkeys=False)

## Dictionary and list utilities

Examples:

    # Merge dictionaries
    d1 = {1: 1, 2: 2, 3: 3, 4: ["a", "b", "c"]}
    d2 = {2: 6, 5: 8, 6: 9, 4: ["d", "e"]}
    result = merge_dictionaries([d1, d2])
    assert result == {1: 1, 2: 6, 3: 3, 4: ["d", "e"], 5: 8, 6: 9}

    # Diff dictionaries
    d1 = {1: 1, 2: 2, 3: 3, 4: {"a": 1, "b": "c"}}
    d2 = {4: {"a": 1, "b": "c"}, 2: 2, 3: 3, 1: 1}
    diff = dict_diff(d1, d2)
    assert diff == {}
    d2[3] = 4
    diff = dict_diff(d1, d2)
    assert diff == {3: (3, 4)}

    # Add element to list in dict
    d = dict()
    dict_of_lists_add(d, "a", 1)
    assert d == {"a": [1]}
    dict_of_lists_add(d, 2, "b")
    assert d == {"a": [1], 2: ["b"]}
    dict_of_lists_add(d, "a", 2)
    assert d == {"a": [1, 2], 2: ["b"]}

    # Add element to set in dict
    d = dict()
    dict_of_sets_add(d, "a", 1)
    assert d == {"a": {1}}
    dict_of_sets_add(d, 2, "b")
    assert d == {"a": {1}, 2: {"b"}}

    # Add element to dict in dict
    d = dict()
    dict_of_dicts_add(d, "a", 1, 3.0)
    assert d == {"a": {1: 3.0}}
    dict_of_dicts_add(d, 2, "b", 5.0)
    assert d == {"a": {1: 3.0}, 2: {"b": 5.0}}

    # Spread items in list so similar items are further apart
    input_list = [3, 1, 1, 1, 2, 2]
    result = list_distribute_contents(input_list)
    assert result == [1, 2, 1, 2, 1, 3]

    # Get values for the same key in all dicts in list
    input_list = [{"key": "d", 1: 5}, {"key": "d", 1: 1}, {"key": "g", 1: 2},
                  {"key": "a", 1: 2}, {"key": "a", 1: 3}, {"key": "b", 1: 5}]
    result = extract_list_from_list_of_dict(input_list, "key")
    assert result == ["d", "d", "g", "a", "a", "b"]

    # Cast either keys or values or both in dictionary to type
    d1 = {1: 2, 2: 2.0, 3: 5, "la": 4}
    assert key_value_convert(d1, keyfn=int) == {1: 2, 2: 2.0, 3: 5, "la": 4}
    assert key_value_convert(d1, keyfn=int, dropfailedkeys=True) == {1: 2, 2: 2.0, 3: 5}
    d1 = {1: 2, 2: 2.0, 3: 5, 4: "la"}
    assert key_value_convert(d1, valuefn=int) == {1: 2, 2: 2.0, 3: 5, 4: "la"}
    assert key_value_convert(d1, valuefn=int, dropfailedvalues=True) == {1: 2, 2: 2.0, 3: 5}

    # Cast keys in dictionary to integer
    d1 = {1: 1, 2: 1.5, 3.5: 3, "4": 4}
    assert integer_key_convert(d1) == {1: 1, 2: 1.5, 3: 3, 4: 4}

    # Cast values in dictionary to integer
    d1 = {1: 1, 2: 1.5, 3: "3", 4: 4}
    assert integer_value_convert(d1) == {1: 1, 2: 1, 3: 3, 4: 4}

    # Cast values in dictionary to float
    d1 = {1: 1, 2: 1.5, 3: "3", 4: 4}
    assert float_value_convert(d1) == {1: 1.0, 2: 1.5, 3: 3.0, 4: 4.0}

    # Average values by key in two dictionaries
    d1 = {1: 1, 2: 1.0, 3: 3, 4: 4}
    d2 = {1: 2, 2: 2.0, 3: 5, 4: 4, 7: 3}
    assert avg_dicts(d1, d2) == {1: 1.5, 2: 1.5, 3: 4, 4: 4}

    # Read and write lists to csv
    l = [[1, 2, 3, "a"],
         [4, 5, 6, "b"],
         [7, 8, 9, "c"]]
    write_list_to_csv(filepath, l, headers=["h1", "h2", "h3", "h4"])
    newll = read_list_from_csv(filepath)
    newld = read_list_from_csv(filepath, headers=1, dict_form=True)
    assert newll == [["h1", "h2", "h3", "h4"], ["1", "2", "3", "a"], ["4", "5", "6", "b"], ["7", "8", "9", "c"]]
    assert newld == [{"h1": "1", "h2": "2", "h4": "a", "h3": "3"},
                    {"h1": "4", "h2": "5", "h4": "b", "h3": "6"},
                    {"h1": "7", "h2": "8", "h4": "c", "h3": "9"}]

    ## Convert command line arguments to dictionary
    args = "a=1,big=hello,1=3"
    assert args_to_dict(args) == {"a": "1", "big": "hello", "1": "3"}

## HTML utilities

These are built on top of BeautifulSoup and simplify its setup.

Examples:

    # Get soup for url with optional kwarg downloader=Download() object
    soup = get_soup("http://myurl", user_agent="test")
    # user agent can be set globally using:
    # UserAgent.set_global("test")
    tag = soup.find(id="mytag")

    # Get text of tag stripped of leading and trailing whitespace
    # and newlines and with &nbsp replaced with space
    result = get_text("mytag")

    # Extract HTML table as list of dictionaries
    result = extract_table(tabletag)

## Comparing files

Compare two files:

    result = compare_files(testfile1, testfile2)
    # Result is of form eg.:
    # ["- coal   ,3      ,7.4    ,'needed'\n",
    #  "?         ^\n",
    #  "+ coal   ,1      ,7.4    ,'notneeded'\n",
    #  "?         ^                +++\n"]

## Emailing

Example of setup and sending email:

    smtp_initargs = {
        "host": "localhost",
        "port": 123,
        "local_hostname": "mycomputer.fqdn.com",
        "timeout": 3,
        "source_address": ("machine", 456),
    }
    username = "user@user.com"
    password = "pass"
    email_config_dict = {
        "connection_type": "ssl",
        "username": username,
        "password": password
    }
    email_config_dict.update(smtp_initargs)

    recipients = ["larry@gmail.com", "moe@gmail.com", "curly@gmail.com"]
    subject = "hello"
    text_body = "hello there"
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
    sender = "me@gmail.com"

    with Email(email_config_dict=email_config_dict) as email:
        email.send(recipients, subject, text_body, sender=sender)

## Logging

The library provides elegant logs to the console with a simple default setup which 
should be adequate for most cases. By default, the log shows `INFO` level and higher. 
This can be changed with `console_log_level`. If `log_file`, a path to a log file, is 
specified then logging will also go to a file. The log level for the file can be
set using `file_log_level` which by default is `ERROR`.

    from hdx.utilities.easy_logging import setup_logging
    ...
    logger = logging.getLogger(__name__)
    setup_logging(console_log_level="DEBUG", log_file="output.log", 
    file_log_level="INFO")

To use logging in your files, simply add the line below to the top of
each Python file:

    logger = logging.getLogger(__name__)

Then use the logger like this:

    logger.debug("DEBUG message")
    logger.info("INFORMATION message")
    logger.warning("WARNING message")
    logger.error("ERROR message")
    logger.critical("CRITICAL error message")

There is a class that allows collecting of errors to be logged later, typically on exit.
It is called ErrorsOnExit and can be used as follows:

    with ErrorsOnExit() as errors:
        ...
        errors.add("MY ERROR MESSAGE")
        ...
        errors.add("ANOTHER ERROR MESSAGE")

The above code will collect the errors, in this case "MY ERROR MESSAGE" and "ANOTHER 
ERROR MESSAGE". On leaving the `with` block, the errors will be logged and the code will
exit with the error code 1 (ie. `sys.exit(1)` will be called). If there are no errors, 
the code will not exit and execution will continue after the `with` block (ie.
`sys.exit(1)` will not be called).

## Path utilities

Examples:

    # Gets temporary directory from environment variable
    # TEMP_DIR and falls back to os function
    temp_folder = get_temp_dir()

    # Gets temporary directory from environment variable
    # TEMP_DIR and falls back to os function,
    # optionally appends the given folder, creates the
    # folder and deletes the folder if exiting 
    # successfully else keeps the folder if there was
    # an exception
    with temp_dir("papa", delete_on_success=True, delete_on_failure=False) as tempdir:
        ...
    # Sometimes it is necessary to be able to resume runs if they fail. The following
    # example creates a temporary folder and iterates through a list of items.
    # On each iteration, the current state of progress is stored in the temporary
    # folder. If the iteration were to fail, the temporary folder is not deleted and
    # on the next run, it will resume where it failed. Once the whole list is iterated
    # through, the temporary folder is deleted.
    # What is returned each iteration is a tuple with 2 dictionaries. The first contains 
    # key folder which is the temporary directory optionally with folder appended (and 
    # created if it doesn't exist). In key progress is held the current position in the 
    # iterator. It also contains the key batch containing a batch code to be passed as
    # the batch parameter in create_in_hdx or update_in_hdx calls. The second dictionary 
    # is the next dictionary in the iterator.
    # The environment variable WHERETOSTART can be set to the starting value for example
    # iso3=SDN in the example below. If it is
    # set to RESET, then the temporary folder is deleted before the run starts to ensure
    # it starts from the beginning.    
    iterator = [{"iso3": "AFG", "name": "Afghanistan"}, {"iso3": "SDN", "name": "Sudan"},
                {"iso3": "YEM", "name": "Yemen"}, {"iso3": "ZAM", "name": "Zambia"}]
    result = list()
    for info, nextdict in progress_storing_tempdir(tempfolder, iterator, "iso3"):
        ...

    # Get current directory of script
    dir = script_dir(ANY_PYTHON_OBJECT_IN_SCRIPT)

    # Get current directory of script with filename appended
    path = script_dir_plus_file("myfile.txt", ANY_PYTHON_OBJECT_IN_SCRIPT)

    # Get filename or (filename, extension) from url
    url = "https://raw.githubusercontent.com/OCHA-DAP/hdx-python-utilities/master/tests/fixtures/test_data.csv"
    filename = get_filename_from_url(fixtureurl)
    assert filename == "test_data.csv"
    filename, extension = get_filename_extension_from_url(fixtureurl)
    assert filename == "test_data"
    assert extension == ".csv"

## Date parsing utilities

Ambiguous dates are parsed as day first D/M/Y where there are values in front of the year and day last Y/M/D
where there are values after the year.

Examples:

    # Parse dates
    assert parse_date("20/02/2013") == datetime(2013, 2, 20, 0, 0)
    assert parse_date("20/02/2013", "%d/%m/%Y") == datetime(2013, 2, 20, 0, 0)
    
    # Parse date ranges
    parse_date_range("20/02/2013")
    # == datetime(2013, 2, 20, 0, 0), datetime(2013, 2, 20, 0, 0)
    parse_date_range("20/02/2013 10:00:00")
    # == datetime(2013, 2, 20, 10, 0), datetime(2013, 2, 20, 10, 0)
    parse_date_range("20/02/2013 10:00:00", zero_time=True)
    # == datetime(2013, 2, 20, 0, 0), datetime(2013, 2, 20, 0, 0)
    parse_date_range("20/02/2013", "%d/%m/%Y")
    # == datetime(2013, 2, 20, 0, 0), datetime(2013, 2, 20, 0, 0)
    parse_date_range("02/2013")
    # == datetime(2013, 2, 1, 0, 0), datetime(2013, 2, 28, 0, 0)
    parse_date_range("2013")
    # == datetime(2013, 1, 1, 0, 0), datetime(2013, 12, 31, 0, 0)
    
    # Pass dict in fuzzy activates fuzzy matching that allows for looking for dates within a sentence
    fuzzy = dict()
    parse_date_range("date is 20/02/2013 for this test", fuzzy=fuzzy)
    # == datetime(2013, 2, 20, 0, 0), datetime(2013, 2, 20, 0, 0)    
    assert fuzzy == {"startdate": datetime(2013, 2, 20, 0, 0), "enddate": datetime(2013, 2, 20, 0, 0), 
                     "nondate": ("date is ", " for this test"), "date": ("20/02/2013",)}
    fuzzy = dict()
    parse_date_range("date is 02/2013 for this test", fuzzy=fuzzy)
    # == datetime(2013, 2, 1, 0, 0), datetime(2013, 2, 28, 0, 0)
    assert fuzzy == {"startdate": datetime(2013, 2, 1, 0, 0), "enddate": datetime(2013, 2, 28, 0, 0), 
                     "nondate": ("date is ", " for this test"), "date": ("02/2013",)}

## Text processing

Examples:

    a = "The quick brown fox jumped over the lazy dog. It was so fast!"
    
    # Remove whitespace and punctuation from end of string
    assert remove_end_characters('lalala,.,"') == "lalala"
    assert remove_end_characters('lalala, .\t/,"', f"{punctuation}{whitespace}" == "lalala"
    
    # Remove list of items from end of string, stripping any whitespace
    result = remove_from_end(a, ["fast!", "so"], "Transforming %s -> %s")
    assert result == "The quick brown fox jumped over the lazy dog. It was"

    # Remove string from another string and delete any preceding end characters - by default 
    # punctuation (eg. comma) and any whitespace following the punctuation
    assert remove_string("lala, 01/02/2020 ", "01/02/2020") == "lala "
    assert remove_string("lala,(01/02/2020) ", "01/02/2020") == "lala) "
    assert remove_string("lala, 01/02/2020 ", "01/02/2020", PUNCTUATION_MINUS_BRACKETS) == "lala "
    assert remove_string("lala,(01/02/2020) ", "01/02/2020", PUNCTUATION_MINUS_BRACKETS) == "lala,() "

    # Replace multiple strings in a string simultaneously
    result = multiple_replace(a, {"quick": "slow", "fast": "slow", "lazy": "busy"})
    assert result == "The slow brown fox jumped over the busy dog. It was so slow!"

    # Extract words from a string sentence into a list
    result = get_words_in_sentence("Korea (Democratic People's Republic of)")
    assert result == ["Korea", "Democratic", "People's", "Republic", "of"]

    # Find matching text in strings
    a = "The quick brown fox jumped over the lazy dog. It was so fast!"
    b = "The quicker brown fox leapt over the slower fox. It was so fast!"
    c = "The quick brown fox climbed over the lazy dog. It was so fast!"
    result = get_matching_text([a, b, c], match_min_size=10)
    assert result == " brown fox  over the  It was so fast!"

    # Search a string for each of a list of strings and return the earliest index
    assert earliest_index(a, ["dog", "lala", "fox", "haha", "quick"]) == 4

## Encoding utilities

Examples:

    # Base 64 encode and decode string
    a = "The quick brown fox jumped over the lazy dog. It was so fast!"
    b = str_to_base64(a)
    c = base64_to_str(b)

## Valid UUID

Examples:

    assert is_valid_uuid("jpsmith") is False
    assert is_valid_uuid("c9bf9e57-1685-4c89-bafb-ff5af830be8a") is True

## Easy building and packaging

The pyproject.toml and setup.cfg provide a template that can be used by other projects. There is a helper 
function in this library, git_tag_whl, which aids with creating a tag in GitHub based on the version in
the wheel file built by tox.
