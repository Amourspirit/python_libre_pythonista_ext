from __future__ import annotations
from typing import cast
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict
from ...log.log_inst import LogInst


class LpFnAssign:
    """
    This is a special rule and is not added to the code_rules list.
    It is used to get the value of the last lp() function call. If it matches.
    """

    def __init__(self) -> None:
        self._result = None
        self.data = None
        self._log = LogInst()

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

        if self.mod is None:
            return False

        if not self.ast_mod:
            return False

        if len(self.ast_mod.body) < 1:
            return False
        last = self.ast_mod.body[-1]
        if not isinstance(last, (ast.Assign, ast.AnnAssign)):
            return False

        try:
            if last.value.func.id != "lp":  # type: ignore
                return False
        except Exception:
            return False

        with self._log.indent(True):
            try:
                self._result = cast(DotDict, self.mod.lp_mod.LAST_LP_RESULT)  # type: ignore
                return True
            except Exception as e:
                self._log.debug("LpFnAssign - get_is_match() Exception: %s", e)
            self._log.debug("LpFnAssign - get_is_match() Not a match. Returning False.")
            return False

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
        self.data = None
        self.ast_mod = None

    def __repr__(self) -> str:
        return "<LpFnAssign()>"
