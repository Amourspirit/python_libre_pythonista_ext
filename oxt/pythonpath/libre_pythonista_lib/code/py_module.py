from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import ast
import copy
import os
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
    from ....___lo_pip___.debug.break_mgr import BreakMgr

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.debug.break_mgr import BreakMgr

    break_mgr = BreakMgr()
    # break_mgr.add_breakpoint("libre_pythonista_lib.code.py_module.init")
    break_mgr.add_breakpoint("libre_pythonista_lib.code.py_module.execute_code")


def is_pytest_running() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


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
        break_mgr.check_breakpoint("libre_pythonista_lib.code.py_module.init")
        self._is_init = False
        self._is_py_test_running = is_pytest_running()
        self._log = OxtLogger(log_name=self.__class__.__name__)

        self.mod = types.ModuleType("PyMod")
        self._cr = CodeRules()
        # _private_enabled should default to True.
        # If this is to be added as a setting it must be at the document level.
        # This way when a document is shared the setting is also shared.
        # If this were a setting, it would have to be on the document level.
        self._private_enabled = False
        self._current_ast_mod = None
        self._current_match_rule = None  # used for testing
        self._init_mod()
        self._is_init = True

    def _init_mod(self) -> None:
        self._log.debug("_init_mod()")
        code = get_module_init_code()
        try:
            self.execute_code(code, self.mod.__dict__)
            self._init_dict = self.mod.__dict__.copy()
            if lp_plot is not None:
                self._init_dict.update(**lp_plot.__dict__.copy())
            else:
                self._log.warning("lp_plot module is not available.")
            self._log.debug("_init_mod() done.")
        except Exception:
            self._log.exception("Error initializing module")
            raise

    def execute_code(self, code_snippet: str, globals: dict | None = None) -> Any:  # noqa: ANN401
        """
        Compiles and executes the given code snippet.
        - If the last statement is an expression, returns its value.
        - Otherwise, returns the value of `result` if it exists in local variables.
        """
        if self._is_init:
            break_mgr.check_breakpoint("libre_pythonista_lib.code.py_module.execute_code")

        try:
            if globals is None:
                globals = {}
            globals["_"] = None
            locals = {}

            # Parse the code as a full module
            tree = ast.parse(code_snippet, mode="exec")
            # needs a copy because may pop the last node below.
            self._current_ast_mod = copy.deepcopy(tree)

            # If the last node is an expression, remove it for separate handling
            last_expr = None
            assign_name = ""
            # print(str(type(tree.body[-1])))
            last_node = tree.body[-1]
            if tree.body and isinstance(last_node, ast.Expr):
                last_expr = cast(ast.Expr, tree.body.pop())
            elif tree.body and isinstance(last_node, ast.Assign):
                last_expr = cast(ast.Assign, tree.body.pop())
                try:
                    assign_name = last_expr.targets[0].id  # type: ignore
                except Exception:
                    assign_name = ""
            elif tree.body and isinstance(last_node, ast.AnnAssign):
                last_expr = cast(ast.Assign, tree.body.pop())
                try:
                    assign_name = last_expr.target.id  # type: ignore
                except Exception:
                    assign_name = ""
            last_node = None

            # Compile all but the last expression as 'exec'
            module_body = ast.fix_missing_locations(ast.Module(body=tree.body, type_ignores=[]))
            exec_code = compile(module_body, "<string>", "exec")

            # Execute statements
            # do not use locals here or the module values will be assigned to locals
            # exec(exec_code, globals, locals)
            exec(exec_code, globals)

            # If there was a final expression node, evaluate it
            if last_expr:
                expr = ast.Expression(last_expr.value)
                expr = ast.fix_missing_locations(expr)
                eval_code = compile(expr, "<string>", "eval")
                result = eval(eval_code, globals, locals)
                if assign_name:
                    if self._private_enabled:
                        if not assign_name.startswith("_"):
                            globals[assign_name] = result
                    else:
                        globals[assign_name] = result

                globals["_"] = result

            # If there's no final expression, fallback to returning locals["_"], if present
            return globals.get("_")

        except SyntaxError as e:
            self._log.exception("Syntax error executing code: \n%s", code_snippet)
            return None

        except Exception as e:
            self._log.exception("Error executing  error: '%s' code: \n%s", e, code_snippet)
            # traceback.print_exc()
            return None

    def reset_module(self) -> None:
        with self._log.indent(True):
            self._log.debug("reset_module()")
        self.mod.__dict__.clear()
        self.mod.__dict__.update(self._init_dict)
        self._current_ast_mod = None
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
            self._log.exception("Error cleaning code: %s", code)
            raise

        result = None
        self._current_match_rule = None  # used for testing
        try:
            if code:
                self._log.debug("Executing code.")
                self.execute_code(code, self.mod.__dict__)
                self._log.debug("Executed code.")
            rule = self._cr.get_matched_rule(self.mod, code, self._current_ast_mod)
            self._log.debug("Got matched rule.")
            result = rule.get_value()
            self._log.debug("Got result.")

            if self._is_py_test_running:
                self._current_match_rule = rule
            else:
                # only reset rule if not testing.
                # The _current_match_rule will contain the last matched rule so do reset it.
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
                            ps_log.error("Error updating module.\n%s\n", code, exc_info=True)
                        else:
                            ps_log.error("%s", e)
                    except Exception as e:
                        self._log.error("LibrePythonistaLog error", exc_info=True)
                    if self._log.is_debug:
                        self._log.warning(
                            "Error updating module. Result set to %s.\n%s\n", result, code, exc_info=True
                        )
                    else:
                        self._log.warning("Error updating module. Result set to %s.\n", result, exc_info=True)
                except Exception:
                    self._log.exception("update_with_result() Error updating module.\n%s\n", code)
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
                self._log.debug("set_global_var(%s, %s)", var_name, value)
        if var_name == "CURRENT_CELL_OBJ":
            self.mod.__dict__["lp_mod"].CURRENT_CELL_OBJ = value
            return
        self.mod.__dict__[var_name] = value
        self.mod.__dict__["_"] = value

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
        self._current_ast_mod = None
        if not code:
            return None
        code = str_util.remove_comments(code)
        code = str_util.clean_string(code)
        if code:
            self.execute_code(code, self.mod.__dict__)
        else:
            return None
        rule = self._cr.get_matched_rule(self.mod, code, self._current_ast_mod)
        result = rule.get_value()
        rule.reset()
        with self._log.indent(True):
            self._log.debug("reset_to_dict() done.")
        return result
