from __future__ import annotations
from typing import Any
import types
import re
from ...utils import str_util


class RegexLastLine:
    """
    A class to to get the attribute value from module if last line of code matches a regex.
    """

    def __init__(self, regex: re.Pattern[str] | None = None) -> None:
        """
        Constructor

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
        """
        self._result = None
        if regex is None:
            self.regex = re.compile(r"^(\w+)\s*=")
        else:
            self.regex = regex
        self.match: re.Match[str] | None = None

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
        """Check if rules is a match for the last line of code."""
        self._result = None
        if not self.code:
            return False
        last_line = str_util.get_last_line(self.code)
        self.match = self.regex.search(last_line)
        if not self.match:
            return False
        var_name = self.match.group(1)
        self._result = getattr(self.mod, var_name, None)
        if callable(self._result):
            self._result = None
        return self._result is not None

    def get_value(self) -> Any:
        """Get the value of matched attribute from module."""
        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self._result = None
        self.mod = None
        self.code = None
