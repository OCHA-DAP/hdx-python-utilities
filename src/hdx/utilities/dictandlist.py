"""Dict and List utilities"""

import itertools
from collections import UserDict
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Union

from hdx.utilities.frictionless_wrapper import get_frictionless_resource
from hdx.utilities.typehint import ListDict, ListTuple


def merge_two_dictionaries(
    a: MutableMapping, b: Mapping, merge_lists: bool = False
) -> MutableMapping:
    """Merges b into a and returns merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen

    Args:
        a (MutableMapping): dictionary to merge into
        b (Mapping): dictionary to merge from
        merge_lists (bool): Whether to merge lists (True) or replace lists (False). Default is False.

    Returns:
        MutableMapping: Merged dictionary
    """
    key = None
    # ## debug output
    # sys.stderr.write(f"DEBUG: {b} to {a}\n")
    try:
        if a is None or isinstance(a, (str, int, float)):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be appended or replaced
            if isinstance(b, list):
                if merge_lists:
                    # merge lists
                    a.extend(b)
                else:
                    # replace list
                    a = b
            else:
                # append to list
                a.append(b)
        elif isinstance(a, (dict, UserDict)):
            # dicts must be merged
            if isinstance(b, (dict, UserDict)):
                for key in b:
                    if key in a:
                        a[key] = merge_two_dictionaries(
                            a[key], b[key], merge_lists=merge_lists
                        )
                    else:
                        a[key] = b[key]
            else:
                raise ValueError(
                    f'Cannot merge non-dict "{b}" into dict "{a}"'
                )
        else:
            raise ValueError(f'NOT IMPLEMENTED "{b}" into "{a}"')
    except TypeError as e:
        raise ValueError(
            f'TypeError "{e}" in key "{key}" when merging "{b}" into "{a}"'
        )
    return a


def merge_dictionaries(
    dicts: ListTuple[MutableMapping], merge_lists: bool = False
) -> MutableMapping:
    """Merges all dictionaries in dicts into a single dictionary and returns result

    Args:
        dicts (List[MutableMapping]): Dictionaries to merge into the first one in the list
        merge_lists (bool): Whether to merge lists (True) or replace lists (False). Default is False.

    Returns:
        MutableMapping: Merged dictionary

    """
    dict1 = dicts[0]
    for other_dict in dicts[1:]:
        merge_two_dictionaries(dict1, other_dict, merge_lists=merge_lists)
    return dict1


def dict_diff(d1: Mapping, d2: Mapping, no_key: str = "<KEYNOTFOUND>") -> Dict:
    """Compares two dictionaries

    Args:
        d1 (Mapping): First dictionary to compare
        d2 (Mapping): Second dictionary to compare
        no_key (str): What value to use if key is not found Defaults to '<KEYNOTFOUND>'.

    Returns:
        Dict: Comparison dictionary

    """
    d1keys = set(d1.keys())
    d2keys = set(d2.keys())
    both = d1keys & d2keys
    diff = {k: (d1[k], d2[k]) for k in both if d1[k] != d2[k]}
    diff.update({k: (d1[k], no_key) for k in d1keys - both})
    diff.update({k: (no_key, d2[k]) for k in d2keys - both})
    return diff


def dict_of_lists_add(
    dictionary: MutableMapping, key: Any, value: Any
) -> None:
    """Add value to a list in a dictionary by key

    Args:
        dictionary (MutableMapping): Dictionary to which to add values
        key (Any): Key within dictionary
        value (Any): Value to add to list in dictionary

    Returns:
        None

    """
    list_objs = dictionary.get(key, list())
    list_objs.append(value)
    dictionary[key] = list_objs


def dict_of_sets_add(dictionary: MutableMapping, key: Any, value: Any) -> None:
    """Add value to a set in a dictionary by key

    Args:
        dictionary (MutableMapping): Dictionary to which to add values
        key (Any): Key within dictionary
        value (Any): Value to add to set in dictionary

    Returns:
        None

    """
    set_objs = dictionary.get(key, set())
    set_objs.add(value)
    dictionary[key] = set_objs


def dict_of_dicts_add(
    dictionary: MutableMapping, parent_key: Any, key: Any, value: Any
) -> None:
    """Add key value pair to a dictionary within a dictionary by key

    Args:
        dictionary (MutableMapping): Dictionary to which to add values
        parent_key (Any): Key within parent dictionary
        key (Any): Key within dictionary
        value (Any): Value to add to set in dictionary

    Returns:
        None

    """
    dict_objs = dictionary.get(parent_key, dict())
    dict_objs[key] = value
    dictionary[parent_key] = dict_objs


def list_distribute_contents_simple(
    input_list: List, function: Callable[[Any], Any] = lambda x: x
) -> List:
    """Distribute the contents of a list eg. [1, 1, 1, 2, 2, 3] -> [1, 2, 3, 1, 2, 1]. List can contain complex types
    like dictionaries in which case the function can return the appropriate value eg.  lambda x: x[KEY]

    Args:
        input_list (List): List to distribute values
        function (Callable[[Any], Any]): Return value to use for distributing. Defaults to lambda x: x.

    Returns:
        List: Distributed list

    """
    dictionary = dict()
    for obj in input_list:
        dict_of_lists_add(dictionary, function(obj), obj)
    output_list = list()
    i = 0
    done = False
    while not done:
        found = False
        for key in sorted(dictionary):
            if i < len(dictionary[key]):
                output_list.append(dictionary[key][i])
                found = True
        if found:
            i += 1
        else:
            done = True
    return output_list


def list_distribute_contents(
    input_list: List, function: Callable[[Any], Any] = lambda x: x
) -> List:
    """Distribute the contents of a list eg. [1, 1, 1, 2, 2, 3] -> [1, 2, 1, 2, 1, 3]. List can contain complex types
    like dictionaries in which case the function can return the appropriate value eg.  lambda x: x[KEY]

    Args:
        input_list (List): List to distribute values
        function (Callable[[Any], Any]): Return value to use for distributing. Defaults to lambda x: x.

    Returns:
        List: Distributed list

    """

    def riffle_shuffle(piles_list):
        def grouper(n, iterable, fillvalue=None):
            args = [iter(iterable)] * n
            return itertools.zip_longest(fillvalue=fillvalue, *args)

        if not piles_list:
            return []
        piles_list.sort(key=len, reverse=True)
        width = len(piles_list[0])
        pile_iters_list = [iter(pile) for pile in piles_list]
        pile_sizes_list = [
            [pile_position] * len(pile)
            for pile_position, pile in enumerate(piles_list)
        ]
        grouped_rows = grouper(
            width, itertools.chain.from_iterable(pile_sizes_list)
        )
        grouped_columns = itertools.zip_longest(*grouped_rows)
        shuffled_pile = [
            next(pile_iters_list[position])
            for position in itertools.chain.from_iterable(grouped_columns)
            if position is not None
        ]
        return shuffled_pile

    dictionary = dict()
    for obj in input_list:
        dict_of_lists_add(dictionary, function(obj), obj)
    intermediate_list = list()
    for key in sorted(dictionary):
        intermediate_list.append(dictionary[key])
    return riffle_shuffle(intermediate_list)


def extract_list_from_list_of_dict(
    list_of_dict: List[Mapping], key: Any
) -> List:
    """Extract a list by looking up key in each member of a list of dictionaries

    Args:
        list_of_dict (List[Mapping]): List of dictionaries
        key (Any): Key to find in each dictionary

    Returns:
        List: List containing values returned from each dictionary

    """
    result = list()
    for dictionary in list_of_dict:
        result.append(dictionary[key])
    return result


def key_value_convert(
    dictin: Mapping,
    keyfn: Callable[[Any], Any] = lambda x: x,
    valuefn: Callable[[Any], Any] = lambda x: x,
    dropfailedkeys: bool = False,
    dropfailedvalues: bool = False,
    exception: Exception = ValueError,
) -> Dict:
    """Convert keys and/or values of dictionary using functions passed in as parameters

    Args:
        dictin (Mapping): Input dictionary
        keyfn (Callable[[Any], Any]): Function to convert keys. Defaults to lambda x: x
        valuefn (Callable[[Any], Any]): Function to convert values. Defaults to lambda x: x
        dropfailedkeys (bool): Whether to drop dictionary entries where key conversion fails. Defaults to False.
        dropfailedvalues (bool): Whether to drop dictionary entries where value conversion fails. Defaults to False.
        exception (Exception): The exception to expect if keyfn or valuefn fail. Defaults to ValueError.

    Returns:
        Dict: New dictionary with converted keys and/or values

    """
    dictout = dict()
    for key in dictin:
        try:
            new_key = keyfn(key)
        except exception:
            if dropfailedkeys:
                continue
            new_key = key
        value = dictin[key]
        try:
            new_value = valuefn(value)
        except exception:
            if dropfailedvalues:
                continue
            new_value = value
        dictout[new_key] = new_value
    return dictout


def integer_key_convert(dictin: Mapping, dropfailedkeys: bool = False) -> Dict:
    """Convert keys of dictionary to integers

    Args:
        dictin (Mapping): Input dictionary
        dropfailedkeys (bool): Whether to drop dictionary entries where key conversion fails. Defaults to False.

    Returns:
        Dict: Dictionary with keys converted to integers

    """
    return key_value_convert(dictin, keyfn=int, dropfailedkeys=dropfailedkeys)


def integer_value_convert(
    dictin: Mapping, dropfailedvalues: bool = False
) -> Dict:
    """Convert values of dictionary to integers

    Args:
        dictin (Mapping): Input dictionary
        dropfailedvalues (bool): Whether to drop dictionary entries where key conversion fails. Defaults to False.

    Returns:
        Dict: Dictionary with values converted to integers

    """
    return key_value_convert(
        dictin, valuefn=int, dropfailedvalues=dropfailedvalues
    )


def float_value_convert(
    dictin: Mapping, dropfailedvalues: bool = False
) -> Dict:
    """Convert values of dictionary to floats

    Args:
        dictin (Mapping): Input dictionary
        dropfailedvalues (bool): Whether to drop dictionary entries where key conversion fails. Defaults to False.

    Returns:
        Dict: Dictionary with values converted to floats

    """
    return key_value_convert(
        dictin, valuefn=float, dropfailedvalues=dropfailedvalues
    )


def avg_dicts(
    dictin1: Mapping, dictin2: Mapping, dropmissing: bool = True
) -> Dict:
    """Create a new dictionary from two dictionaries by averaging values

    Args:
        dictin1 (Mapping): First input dictionary
        dictin2 (Mapping): Second input dictionary
        dropmissing (bool): Whether to drop keys missing in one dictionary. Defaults to True.

    Returns:
        Dict: Dictionary with values being average of 2 input dictionaries

    """
    dictout = dict()
    for key in dictin1:
        if key in dictin2:
            dictout[key] = (dictin1[key] + dictin2[key]) / 2
        elif not dropmissing:
            dictout[key] = dictin1[key]
    if not dropmissing:
        for key in dictin2:
            if key not in dictin1:
                dictout[key] = dictin2[key]
    return dictout


def read_list_from_csv(
    url: str,
    headers: Union[int, ListTuple[int], ListTuple[str], None] = None,
    dict_form: bool = False,
    **kwargs: Any,
) -> List[ListDict]:
    """Read a list of rows in dict or list form from a csv. The headers argument is
    either a row number or list of row numbers (in case of multi-line headers) to be
    considered as headers (rows start counting at 1), or the actual headers defined as
    a list of strings. If not set, all rows will be treated as containing values.

    Args:
        url (str): URL or path to read from
        headers (Union[int, ListTuple[int], ListTuple[str], None]): Row number of headers. Defaults to None.
        dict_form (bool): Return dict (requires headers parameter) or list for each row. Defaults to False (list)
        **kwargs: Other arguments to pass to Tabulator Stream

    Returns:
        List[ListDict]: List of rows in dict or list form

    """
    if dict_form and headers is None:
        raise ValueError("If dict_form is True, headers must not be None!")
    resource = get_frictionless_resource(url, headers=headers, **kwargs)
    result = list()
    if not dict_form:
        result.append(resource.header)
    for inrow in resource.row_stream:
        if dict_form:
            row = inrow.to_dict()
        else:
            row = inrow.to_list()
        result.append(row)
    resource.close()
    return result


def write_list_to_csv(
    filepath: str,
    rows: List[ListDict],
    headers: Union[int, ListTuple[str], None] = None,
    columns: Union[ListTuple[int], ListTuple[str], None] = None,
) -> None:
    """Write a list of rows in dict or list form to a csv. (The headers argument is
    either a row number (rows start counting at 1), or the actual headers defined as a
    list of strings. If not set, all rows will be treated as containing values.)

    Args:
        filepath (str): Path to write to
        rows (List[ListDict]): List of rows in dict or list form
        headers (Union[int, ListTuple[str], None]): Headers to write. Defaults to None.
        columns (Union[ListTuple[int], ListTuple[str], None]): Columns to write. Defaults to all.

    Returns:
        None

    """
    if len(rows) != 0:
        row = rows[0]
        if isinstance(row, dict):
            has_header = True
            if columns:
                newrows = list()
                for row in rows:
                    newrow = dict()
                    for column in columns:
                        if column in row:
                            newrow[column] = row[column]
                    newrows.append(newrow)
                rows = newrows
                if headers is None:
                    headers = columns
        else:
            if headers is None:
                headers = 1
            if isinstance(headers, int):
                rowno = headers
                headers = rows[rowno - 1]
                rows = rows[rowno:]
            has_header = False
            if columns:
                newrows = list()
                for row in rows:
                    newrow = list()
                    for column in columns:
                        newrow.append(row[column - 1])
                    newrows.append(newrow)
                rows = newrows
        resource = get_frictionless_resource(
            data=rows,
            has_header=has_header,
            headers=headers,
        )
        resource.write(filepath, format="csv")
        resource.close()


def args_to_dict(args: str) -> Dict:
    """Convert command line arguments in a comma separated string to a dictionary

    Args:
        args (str): Command line arguments

    Returns:
        Dict: Dictionary of arguments

    """
    arguments = dict()
    for arg in args.split(","):
        key, value = arg.split("=")
        arguments[key] = value
    return arguments
