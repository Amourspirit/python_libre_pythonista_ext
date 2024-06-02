from __future__ import annotations
from typing import Any
import types


class LastDict:
    """
    A class to represent the last dictionary item in a module.
    """

    def __init__(self) -> None:
        pass

    def set_values(self, mod: types.ModuleType, code: str) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
        """
        self.mod = mod
        self.code = code

    def get_is_match(self) -> bool:
        """Check if rules is a match. For this rule the return result is always True."""
        return True

    def get_value(self) -> Any:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        last_key = next(reversed(self.mod.__dict__), None)
        if last_key is None:
            return None
        result = getattr(self.mod, last_key)
        if callable(result):
            return None
        return result
