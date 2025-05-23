from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import ast
import types
import re
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils import str_util
else:
    from libre_pythonista_lib.utils import str_util


class RegexLastLine:
    """
    A class to to get the attribute value from module if last line of code matches a regex.
    """

    def __init__(self, regex: Optional[re.Pattern[str]] = None, use_match_value: bool = False) -> None:
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
        self.use_match_value = use_match_value
        self.match: Optional[re.Match[str]] = None

    def set_values(self, mod: types.ModuleType, code: str, ast_mod: Optional[ast.Module]) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
            ast_mod (ast.Module, None): AST module.
        """
        self._result = None
        self.mod = mod
        self.code = code
        self.ast_mod = ast_mod

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
        result = DotDict(data=var_name) if self.use_match_value else DotDict(data=getattr(self.mod, var_name, None))
        if not callable(result.data):
            self._result = result
        return self._result is not None

    def get_value(self) -> DotDict:
        """Get the value of matched attribute from module."""
        if self._result is None:
            return DotDict(data=None)

        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self._result = None
        self.mod = None
        self.code = None
        self.ast_mod = None

    def __repr__(self) -> str:
        return "<RegexLastLine()>"
