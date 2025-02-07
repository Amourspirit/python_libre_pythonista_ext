from __future__ import annotations
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict


class Expr:
    """
    Match the last expression node in the AST module.
    Expected to match ``sum(1, 2)`` but not ``result = sum(1, 2)``.
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
        """Check if rules is a match."""
        self._result = None
        if not self.code:
            return False
        if not self.ast_mod:
            return False
        if len(self.ast_mod.body) < 1:
            return False
        is_instance = isinstance(self.ast_mod.body[-1], ast.Expr)
        if is_instance:
            self._result = DotDict(data=self.mod.__dict__.get("_"))
            return True
        return False

    def get_value(self) -> DotDict:
        """
        Retrieves a value from the module's dictionary.

        Returns:
            DotDict: A DotDict object containing the value associated with the key "_" in the module's dictionary.
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
        return "<Expr()>"
