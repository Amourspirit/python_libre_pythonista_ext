from __future__ import annotations
from typing import Any, TYPE_CHECKING
import importlib.util

# import importlib
import types
from ooodev.utils.helper.dot_dict import DotDict

# from ooodev.utils.builder.dynamic_importer import DynamicImporter
from ..utils import str_util
from .rules.code_rules import CodeRules

from .mod_helper.lplog import LpLog as LibrePythonistaLog
from ..cell.errors.general_error import GeneralError


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


def is_import_available(module_name: str, class_name: str = "", alias: str = "") -> bool:
    spec = importlib.util.find_spec(module_name)
    return spec is not None


try:
    if is_import_available("matplotlib"):
        from .mod_helper import lp_plot
    else:
        lp_plot = None
except ImportError:
    lp_plot = None


def get_module_init_code() -> str:
    # See https://matplotlib.org/stable/users/explain/figure/backends.html
    # for more information on the matplotlib backend.
    pre_lines = [
        "from __future__ import annotations",
        "from typing import Any, cast, TYPE_CHECKING",
    ]
    code_lines = []
    if is_import_available("matplotlib"):
        code_lines.append("import matplotlib")
        code_lines.append("matplotlib.use('svg')")
        # code_lines.append("matplotlib.use('agg')")
        code_lines.append("from matplotlib import pyplot as plt")
    if is_import_available("pandas"):
        code_lines.append("import pandas as pd")
        code_lines.append("pd.options.plotting.backend = 'matplotlib'")
    if is_import_available("numpy"):
        code_lines.append("import numpy as np")
    post_lines = [
        "from ooodev.loader import Lo",
        "from ooodev.calc import CalcDoc",
        "from ooodev.calc import CalcSheet",
        "from ooodev.utils.data_type.cell_obj import CellObj",
        "from ooodev.utils.data_type.range_obj import RangeObj",
        "from ___lo_pip___.oxt_logger import OxtLogger",
        "from ___lo_pip___.debug.break_mgr import BreakMgr",
        "from ___lo_pip___.debug.break_mgr import check_breakpoint",
        "from libre_pythonista_lib.log.log_inst import LogInst",
        "from libre_pythonista_lib.code.mod_helper import lp_mod",
        "from libre_pythonista_lib.code.mod_helper.lp_mod import lp",
        "from libre_pythonista_lib.code.mod_helper.lplog import StaticLpLog as lp_log, LpLog as LibrePythonistaLog",
        "from libre_pythonista_lib.code.mod_helper import lp_plot",
        "PY_ARGS = None",
        "CURRENT_CELL_OBJ = None",
        "CURRENT_CELL_ID = ''",
        "DUMMY_LAST_VALUE = None",
    ]
    lines = pre_lines + code_lines + post_lines
    return "\n".join(lines)


class PyModule:
    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)

        self.mod = types.ModuleType("PyMod")
        self._cr = CodeRules()
        self._init_mod()

    def _init_mod(self) -> None:
        self._log.debug("_init_mod()")
        code = get_module_init_code()
        # from .mod_fn import lp
        try:
            # t = threading.Thread(target=exec, args=(code, self.mod.__dict__), daemon=True)
            # t.start()
            # t.join()
            exec(code, self.mod.__dict__)
            # setattr(self.mod, "lp", lp.lp)
            self._init_dict = self.mod.__dict__.copy()
            if lp_plot is not None:
                self._init_dict.update(**lp_plot.__dict__.copy())
            else:
                self._log.warning("lp_plot module is not available.")
            self._log.debug(f"_init_mod() done.")
        except Exception:
            self._log.exception("Error initializing module")
            raise
        # setattr(self.mod, "np", np)
        # setattr(self.mod, "Lo", lo)
        # setattr(self.mod, "XSCRIPTCONTEXT", Lo.XSCRIPTCONTEXT)
        # setattr(self.mod, "CalcDoc", CalcDoc)

    def reset_module(self) -> None:
        with self._log.indent(True):
            self._log.debug("reset_module()")
        self.mod.__dict__.clear()
        self.mod.__dict__.update(self._init_dict)
        with self._log.indent(True):
            self._log.debug("reset_module() done.")

    def update_with_result(self, code: str = "") -> DotDict:
        """
        Appends code to current module and returns the last variable in the module.

        Args:
            code (str, optional): Any valid python code

        Returns:
            Any: The last variable in the module if any; Otherwise, None.

        Note:
            If there is an error the result will be a DotDict with ``data=GeneralError(e)`` and ``error=True`` the error.
        """
        with self._log.indent(True):
            self._log.debug("update_with_result() Entered.")
        try:
            code = str_util.remove_comments(code)
            code = str_util.clean_string(code)
            # self._log.debug(f"Cleaned code. \n{code}")
        except Exception:
            self._log.exception(f"Error cleaning code: {code}")
            raise

        result = None
        try:
            if code:
                self._log.debug("Executing code.")
                # run exec in a new thread and wait for it to finish
                # t = threading.Thread(target=exec, args=(code, self.mod.__dict__), daemon=True)
                # t.start()
                # t.join()
                exec(code, self.mod.__dict__)
                self._log.debug("Executed code.")
            rule = self._cr.get_matched_rule(self.mod, code)
            self._log.debug("Got matched rule.")
            result = rule.get_value()
            self._log.debug("Got result.")
            rule.reset()
            self._log.debug("Reset rule.")
            return result
        # other exceptions can be caught and new error classes can be created.
        except Exception as e:
            with self._log.indent(True):
                try:
                    # result will be assigned to the py_source.value Other rules for the cell will handle this.
                    result = DotDict(data=GeneralError(e), error=True)
                    try:
                        lp_log_inst = LibrePythonistaLog()
                        ps_log = lp_log_inst.log
                        if lp_log_inst.log_extra_info:
                            ps_log.error(f"Error updating module.\n{code}\n", exc_info=True)
                        else:
                            ps_log.error(f"{e}")
                    except Exception as e:
                        self._log.error(f"LibrePythonistaLog error", exc_info=True)
                    if self._log.is_debug:
                        self._log.warning(f"Error updating module. Result set to {result}.\n{code}\n", exc_info=True)
                    else:
                        self._log.warning(f"Error updating module. Result set to {result}.\n", exc_info=True)
                except Exception:
                    self._log.exception(f"update_with_result() Error updating module.\n{code}\n")
                    raise
        return result

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a global variable in the module.

        Args:
            var_name (str): The name of the variable
            value (Any): The value of the variable
        """
        if self._log.is_debug:
            with self._log.indent(True):
                self._log.debug(f"set_global_var({var_name}, {value})")
        if var_name == "CURRENT_CELL_OBJ":
            self.mod.__dict__["lp_mod"].CURRENT_CELL_OBJ = value
        self.mod.__dict__[var_name] = value

    def reset_to_dict(self, mod_dict: dict, code: str = "") -> Any:  # noqa: ANN401
        """
        Reset the module to the given dictionary and returns the last variable in the module if code is present.

        Args:
            mod_dict (dict): A dictionary of variables to reset the module to.
            code (str, optional): Any valid python code

        Returns:
            Any: If there is code the last variable in the module if any; Otherwise, None.
        """
        with self._log.indent(True):
            self._log.debug("reset_to_dict()")
        self.mod.__dict__.clear()
        self.mod.__dict__.update(mod_dict)
        if not code:
            return None
        code = str_util.remove_comments(code)
        code = str_util.clean_string(code)
        if code:
            exec(code, self.mod.__dict__)
        else:
            return None
        rule = self._cr.get_matched_rule(self.mod, code)
        result = rule.get_value()
        rule.reset()
        with self._log.indent(True):
            self._log.debug("reset_to_dict() done.")
        return result
