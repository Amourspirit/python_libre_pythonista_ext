from __future__ import annotations
import contextlib
import types
from ooodev.utils.helper.dot_dict import DotDict
from ...utils import str_util


class ListFn:
    """
    A class to get the last function only call of a module.
    Expected to match ``sum(1, 2)``.
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
        """Check if rules is a match."""
        self._result = None
        if not self.code:
            return False
        # log = LogInst()

        last_line = str_util.get_last_line(str_util.clean_string(self.code))
        # log.debug(f"AnyFn - get_is_match() last line: {last_line}")
        if str_util.starts_with_whitespace(last_line):
            # log.debug(f"AnyFn - get_is_match() starts with whitespace. Not a match.")
            return False
        if "=" in last_line:
            # log.debug(f"AnyFn - get_is_match() has assignment. Not a match.")
            return False

        self._result = None
        is_list = False
        with contextlib.suppress(Exception):
            glbs = self.mod.__dict__.copy()
            exec(f"some_kinda_var = {last_line}", glbs)
            result = glbs.get("some_kinda_var", None)
            is_list = isinstance(result, list)
            self._result = DotDict(data=result)
        # except Exception as e:
        #     log.debug(f"AnyFn - get_is_match() exception: {e}")
        return is_list

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
        return f"<ListFn()>"
