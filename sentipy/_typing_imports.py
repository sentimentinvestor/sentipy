"""Use typing module where required for python < 3.9.

This deals with the typing module being depreciated.
"""

import sys
from typing import Any

PYTHON_AT_LEAST_3_9 = sys.version_info >= (3, 9)

if PYTHON_AT_LEAST_3_9:
    DictType = dict
    ListType = list
    SetType = set
else:
    from typing import Dict, List, Set

    DictType = Dict
    ListType = List
    SetType = Set
