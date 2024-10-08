from __future__ import annotations
import types
from ooodev.utils.helper.dot_dict import DotDict
from ...utils import str_util


class CodeEmpty:
    """
    A class to get the last function only call of a module.
    Expected to match ``sum(1, 2)``.
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
        # if there is no code yet then this is a new cell and thus empty is a match.
        if not self.code:
            return True
        # log = LogInst()
        if not self.code:
            return True

        code = str_util.clean_string(self.code)
        return code == ""

    def get_value(self) -> DotDict:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        if self._result is None:
            return DotDict(data=None)
        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self._result = None
        self.mod = None
        self.code = None

    def __repr__(self) -> str:
        return f"<CodeEmpty()>"
