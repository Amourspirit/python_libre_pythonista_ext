from __future__ import annotations
from typing import TypeVar


class _Null:
    def __bool__(self) -> bool:
        return False


NULL = _Null()
"""
Null Object uses when None is not an option. Truthy value is ``False``

.. code-block:: python

    if NULL:
        print("This will never be printed")

    if not NULL:
        print("This will always be printed")
"""

TNull = TypeVar("TNull", bound=_Null)
