from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING, Protocol
import ast
import copy
import os
import importlib.util

# import importlib
import types
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.cell.errors.general_error import GeneralError
    from oxt.pythonpath.libre_pythonista_lib.code.mod_helper.lplog import LpLog as LibrePythonistaLog
    from oxt.pythonpath.libre_pythonista_lib.code.rules.code_rules import CodeRules
    from oxt.pythonpath.libre_pythonista_lib.utils import str_util
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from libre_pythonista_lib.cell.errors.general_error import GeneralError
    from libre_pythonista_lib.code.mod_helper.lplog import LpLog as LibrePythonistaLog
    from libre_pythonista_lib.code.rules.code_rules import CodeRules
    from libre_pythonista_lib.utils import str_util
    from libre_pythonista_lib.log.log_mixin import LogMixin

    break_mgr = BreakMgr()
    # break_mgr.add_breakpoint("libre_pythonista_lib.code.py_module.init")
    break_mgr.add_breakpoint("libre_pythonista_lib.code.py_module.execute_code")


class PyModuleT(Protocol):
    def copy_dict(self) -> Dict[str, Any]:
        """Returns a copy of the module dictionary."""
        ...

    def execute_code(self, code_snippet: str, globals: dict | None = None) -> Any:  # noqa: ANN401
        """
        Compiles and executes the given code snippet.
        - If the last statement is an expression, returns its value.
        - Otherwise, returns the value of `result` if it exists in local variables.
        """
        ...

    def reset_module(self) -> None:
        """Reset the module to its initial state."""
        ...

    def update_with_result(self, code: str = "") -> DotDict[Any]:
        """
        Appends code to current module and returns the last variable in the module.

        Args:
            code (str, optional): Any valid python code

        Returns:
            Any: The last variable in the module if any; Otherwise, None.

        Note:
            If there is an error the result will be a DotDict with ``data=GeneralError(e)`` and ``error=True`` the error.
        """
        ...

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a global variable in the module.

        Args:
            var_name (str): The name of the variable
            value (Any): The value of the variable
        """
        ...

    def reset_to_dict(self, mod_dict: Dict[str, Any], code: str = "") -> Any:  # noqa: ANN401
        """
        Reset the module to the given dictionary and returns the last variable in the module if code is present.

        Args:
            mod_dict (dict): A dictionary of variables to reset the module to.
            code (str, optional): Any valid python code

        Returns:
            Any: If there is code the last variable in the module if any; Otherwise, None.
        """
        ...
