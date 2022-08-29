from typing import Dict, List, Tuple, TypeVar, Union

T = TypeVar("T")
ListTuple = Union[List[T], Tuple[T, ...]]
ListDict = Union[List, Dict]
ListTupleDict = Union[List, Tuple, Dict]
