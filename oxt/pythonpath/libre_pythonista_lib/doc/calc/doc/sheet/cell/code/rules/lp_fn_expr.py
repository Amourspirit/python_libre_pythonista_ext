from __future__ import annotations
from typing import cast, TYPE_CHECKING, Optional
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils import str_util
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
else:
    from libre_pythonista_lib.utils import str_util
    from libre_pythonista_lib.log.log_inst import LogInst


class LpFnExpr:
    """
    A class to represent the last dictionary item in a module.
    """

    def __init__(self) -> None:
        self._result = None

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
        """Check if rules is a match."""
        self._result = None
        if not self.code:
            return False
        if not self.ast_mod:
            return False
        if len(self.ast_mod.body) < 1:
            return False
        last = self.ast_mod.body[-1]
        if not isinstance(last, ast.Expr):
            return False
        try:
            if last.value.func.id != "lp":  # type: ignore
                return False
        except Exception:
            return False

        log = LogInst()
        log.debug("LpFn - get_is_match() Entered.")

        result = None
        # with contextlib.suppress(Exception):
        try:
            if "lp_mod" in self.mod.__dict__:
                log.debug("LpFn - get_is_match() lp_mod is in module")
                result = cast(DotDict, self.mod.lp_mod.LAST_LP_RESULT)  # type: ignore
                log.debug("LpFn - get_is_match() lp_mod.LAST_LP_RESULT %s", result)
                if "headers" in result:
                    log.debug("LpFnObj - get_is_match() has headers: %s", result.headers)
            else:
                log.debug("LpFn - get_is_match() lp_mod is NOT in module")
            self._result = result
        except Exception as e:
            log.error("LpFn - get_is_match() Exception: %s", e, exc_info=True)
        return self._result is not None

    def get_value(self) -> DotDict:
        """
        Retrieves a value from the module's dictionary.

        Returns:
            DotDict: A DotDict object containing the value associated with the module's Last item in the dictionary.
        """
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
        return "<LpFnExpr()>"
