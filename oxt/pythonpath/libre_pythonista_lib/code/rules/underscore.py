from __future__ import annotations
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict


class Underscore:
    """
    A class to represent the last dictionary item in a module.
    """

    def __init__(self) -> None:
        self._result = None

    def set_values(self, mod: types.ModuleType, code: str, ast_mod: ast.Module | None) -> None:
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
        """Check if rules is a match. For this rule the return result is always True."""
        self._result = DotDict(data=self.mod.__dict__.get("_"))
        return True

    def get_value(self) -> DotDict:
        """
        Retrieves the value of the ``_`` attribute in the module.

        Returns:
            DotDict: An object containing the value of the last ``_`` in the module, or ``None``.
        """
        if self._result is None:
            self._result = DotDict(data=self.mod.__dict__.get("_"))
        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self.mod = None
        self.code = None
        self.ast_mod = None
        self._result = None

    def __repr__(self) -> str:
        return "<LastDict()>"
