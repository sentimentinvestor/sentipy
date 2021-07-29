"""Use typing module where required for python < 3.9, and defines additional types.

This deals with the typing module being depreciated.
"""

import sys
from typing import Any

PYTHON_AT_LEAST_3_9 = sys.version_info >= (3, 9)

# Initialised first with Any to make mypy happy
# See https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
DictType: Any = None
IterableType: Any = None
ListType: Any = None
SetType: Any = None
TupleType: Any = None

if PYTHON_AT_LEAST_3_9:
    from collections.abc import Iterable

    DictType = dict
    IterableType = Iterable
    ListType = list
    SetType = set
    TupleType = tuple
else:
    from typing import Dict, Iterable, List, Set, Tuple

    DictType = Dict
    IterableType = Iterable
    ListType = List
    SetType = Set
    TupleType = Tuple

# See https://github.com/python/typing/issues/182
# Maybe convert to TypedDict at some point?
JSONType = DictType[str, Any]
