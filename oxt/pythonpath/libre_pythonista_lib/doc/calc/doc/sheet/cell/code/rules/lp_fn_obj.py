from __future__ import annotations
from typing import cast, TYPE_CHECKING, Optional
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.utils import str_util
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from libre_pythonista_lib.utils import str_util
    from libre_pythonista_lib.log.log_inst import LogInst

    break_mgr = BreakMgr()
    # break_mgr.add_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_obj.get_is_match")


class LpFnObj:
    """
    A class to represent the last dictionary item in a module.
    """

    def __init__(self) -> None:
        self._result = None
        self.mod = None
        self.code = None
        self.ast_mod = None

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
        if not isinstance(last, ast.expr):
            return False

        try:
            if last.value.func.id != "lp":  # type: ignore
                return False
        except Exception:
            return False

        break_mgr.check_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_obj.get_is_match")

        log = LogInst()
        log.debug("LpFnObj - get_is_match() Entered.")

        last_lp = self.code.rfind("lp(")
        if last_lp < 0:
            log.debug("LpFnObj - get_is_match() No lp() found: %s", last_lp)
            return False

        # get the substring from the last_lp index.
        # s = str_util.get_str_from_index(self.code, last_lp)
        s = str_util.get_str_from_index(self.code, last_lp)
        # find the next index of )
        next_bracket_index = s.find(")")
        if next_bracket_index < 0:
            return False

        if next_bracket_index == len(s) - 1:
            log.debug("LpFnObj - get_is_match() Last bracket is not the end of the string: %s", next_bracket_index)
            return False

        result = None
        # with contextlib.suppress(Exception):
        try:
            if "lp_mod" in self.mod.__dict__:
                log.debug("LpFnObj - get_is_match() lp_mod is in module")
                flat_line = str_util.flatten_str(s)
                log.debug("LpFnObj - get_is_match() flat_line: %s", flat_line)
                first_index = flat_line.find(")")
                if first_index < 0:
                    log.debug("LpFnObj - get_is_match() flat_line index of ) Not Found")
                    return False
                # get the flat_line after the first index
                short_line = flat_line[first_index + 1 :]
                new_line = f"result = lp_mod.LAST_LP_RESULT.data{short_line}"
                new_line += "\ndot_dictionary = lp_mod.LAST_LP_RESULT"
                mod_copy = self.mod.__dict__.copy()
                exec(new_line, mod_copy)
                result = mod_copy["result"]
                dd = cast(DotDict, mod_copy["dot_dictionary"])
                headers = bool(dd.get("headers", False))
                dd.headers = headers
                dd.data = result
                log.debug("LpFnObj - get_is_match() has headers: %s", dd.headers)

            else:
                dd = None
                log.debug("LpFnObj - get_is_match() lp_mod is NOT in module")
            self._result = dd
        except Exception as e:
            log.error("LpFnObj - get_is_match() Exception: %s", e, exc_info=True)
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
        return "<LpFnObj()>"
