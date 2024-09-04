from __future__ import annotations
from typing import Protocol
from ooodev.utils.helper.dot_dict import DotDict
import types


class CodeRuleT(Protocol):
    """
    A class to represent a code rule.
    """

    def set_values(self, mod: types.ModuleType, code: str) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
        """
        ...

    def get_is_match(self) -> bool:
        """Check if the code matches the rule"""
        ...

    def get_value(self) -> DotDict:
        """
        Gets the value from the module.
        Result is in ``DotDict.data`` key.
        """
        ...

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        ...
