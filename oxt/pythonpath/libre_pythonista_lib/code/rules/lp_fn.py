from __future__ import annotations
from typing import Any
from ooodev.utils.gen_util import NULL_OBJ
import types
from ...utils import str_util
from ...log.log_inst import LogInst


class LpFn:
    """
    A class to represent the last dictionary item in a module.
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
        if not self.code:
            return False
        log = LogInst()

        last_lp = self.code.rfind("lp(")
        if last_lp < 0:
            log.debug(f"LpFn - get_is_match() No lp() found: {last_lp}")
            return False

        # get the substring from the last_lp index.
        s = str_util.get_str_from_index(self.code, last_lp)
        # find the next index of )
        next_bracket_index = s.find(")")
        if next_bracket_index < 0:
            return False

        if next_bracket_index != len(s) - 1:
            log.debug(f"LpFn - get_is_match() Last bracket is not the end of the string: {next_bracket_index}")
            return False

        result = NULL_OBJ
        # with contextlib.suppress(Exception):
        try:
            if "lp_mod" in self.mod.__dict__:
                log.debug("LpFn - get_is_match() lp_mod is in module")
                result = self.mod.lp_mod.LAST_LP_RESULT  # type: ignore
                log.debug(f"LpFn - get_is_match() lp_mod.LAST_LP_RESULT {result}")
            else:
                log.debug("LpFn - get_is_match() lp_mod is NOT in module")
            self._result = result
        except Exception as e:
            log.error(f"LpFn - get_is_match() Exception: {e}", exc_info=True)
        return result is not NULL_OBJ

    def get_value(self) -> Any:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        if self._result is NULL_OBJ:
            return None
        return self._result

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self._result = None
        self.mod = None
        self.code = None

    def __repr__(self) -> str:
        return f"<LpFn()>"
