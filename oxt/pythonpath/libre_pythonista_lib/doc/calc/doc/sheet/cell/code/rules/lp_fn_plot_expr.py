from __future__ import annotations
from typing import cast, TYPE_CHECKING
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
else:
    from libre_pythonista_lib.log.log_inst import LogInst


class LpFnPlotExpr:
    """
    A class to represent ``plt.show()``.
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
            if last.value.func.value.id != "plt":  # type: ignore
                return False
        except Exception:
            return False
        try:
            if last.value.func.attr != "show":  # type: ignore
                return False
        except Exception:
            return False

        log = LogInst()
        log.debug("LpFnPlotExpr - get_is_match() Entered.")

        try:
            dd = DotDict(data=None)
            if "lp_plot" in self.mod.__dict__:
                log.debug("LpFnPlotExpr - get_is_match() lp_plot is in module")
                if isinstance(self.mod.lp_plot.LAST_LP_RESULT, DotDict):  # type: ignore
                    dd = cast(DotDict, self.mod.lp_plot.LAST_LP_RESULT.copy())  # type: ignore
            else:
                log.debug("LpFnPlotExpr - get_is_match() lp_plot is NOT in module")
            self._result = dd
        except Exception as e:
            log.error("LpFnPlotExpr - get_is_match() Exception: %s", e, exc_info=True)
        return self._result is not None

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
        self.ast_mod = None

    def __repr__(self) -> str:
        return "<LpFnPlotExpr()>"
