from __future__ import annotations
from typing import cast
from ooodev.utils.helper.dot_dict import DotDict
import types
from ...utils import str_util
from ...log.log_inst import LogInst


class LpFnPlot:
    """
    A class to represent the plt.show().
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
        log.debug(f"LpFnPlot - get_is_match() Entered.")
        code = str_util.clean_string(self.code)

        # plt.show()
        # if log.is_debug:
        #     log.debug(f"LpFnPlot - get_is_match() code:\n{code}")
        last_lp = code.rfind("plt.show(")
        if last_lp < 0:
            log.debug(f"LpFnPlot - get_is_match() No plt.show() found: {last_lp}")
            return False

        # get the substring from the last_lp index.
        s = str_util.get_str_from_index(code, last_lp).rstrip()
        # log.debug(f"LpFnPlot - get_is_match() s: {s}")
        # find the next index of )
        next_bracket_index = s.find(")")
        if next_bracket_index < 0:
            return False

        if next_bracket_index != len(s) - 1:
            log.debug(f"LpFnPlot - get_is_match() Last bracket is not the end of the string: {next_bracket_index}")
            return False

        try:
            if "lp_plot" in self.mod.__dict__:
                log.debug("LpFnPlot - get_is_match() lp_plot is in module")
                flat_line = str_util.flatten_str(s)
                log.debug(f"LpFnPlot - get_is_match() flat_line: {flat_line}")
                first_index = flat_line.find(")")
                if first_index < 0:
                    log.debug("LpFnPlot - get_is_match() flat_line index of ) Not Found")
                    return False
                # get the flat_line after the first index
                short_line = flat_line[first_index + 1 :]
                new_line = f"result = lp_plot.LAST_LP_RESULT.data{short_line}"
                new_line += "\ndot_dictionary = lp_plot.LAST_LP_RESULT"
                mod_copy = self.mod.__dict__.copy()
                exec(new_line, mod_copy)
                dd = cast(DotDict, mod_copy["dot_dictionary"])
            else:
                log.debug("LpFnPlot - get_is_match() lp_plot is NOT in module")
            self._result = dd
        except Exception as e:
            log.error(f"LpFnPlot - get_is_match() Exception: {e}", exc_info=True)
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

    def __repr__(self) -> str:
        return f"<LpFnPlot()>"
