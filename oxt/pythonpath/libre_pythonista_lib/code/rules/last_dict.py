from __future__ import annotations
import types
from ooodev.utils.helper.dot_dict import DotDict


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

    def get_value(self) -> DotDict:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        last_key = next(reversed(self.mod.__dict__), None)
        if last_key is None:
            return DotDict(data=None)
        result = getattr(self.mod, last_key)
        if callable(result):
            return DotDict(data=None)
        return DotDict(data=result)

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self.mod = None
        self.code = None

    def __repr__(self) -> str:
        return f"<LastDict()>"
