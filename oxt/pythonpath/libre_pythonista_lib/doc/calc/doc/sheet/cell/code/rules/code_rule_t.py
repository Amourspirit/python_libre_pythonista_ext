from __future__ import annotations
import ast
from typing import Protocol
from ooodev.utils.helper.dot_dict import DotDict
import types


class CodeRuleT(Protocol):
    """
    A class to represent a code rule.
    """

    def set_values(self, mod: types.ModuleType, code: str, ast_mod: ast.Module | None) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
            ast_mod (ast.Module, None): AST module
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
