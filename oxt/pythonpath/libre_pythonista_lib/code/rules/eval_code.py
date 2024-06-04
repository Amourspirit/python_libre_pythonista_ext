from __future__ import annotations
from typing import Any
import contextlib
import types
from ...utils import str_util


class EvalCode:
    """
    A class to represent the last dictionary item in a module.
    """

    def __init__(self) -> None:
        self._result = None

    def set_values(self, mod: types.ModuleType, code: str) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
        """
        self._result = None
        self.mod = mod
        self.code = code

    def get_is_match(self) -> bool:
        """Check if rules is a match. For this rule the return result is always True."""
        self._result = None
        if not self.code:
            return False
        last_line = str_util.get_last_line(self.code)
        if str_util.starts_with_whitespace(last_line):
            return False
        result = None
        with contextlib.suppress(Exception):
            glbs = globals().copy()
            result = eval(last_line, glbs)
            self._result = result
        return result is not None

    def get_value(self) -> Any:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self._result = None
        self.mod = None
        self.code = None
