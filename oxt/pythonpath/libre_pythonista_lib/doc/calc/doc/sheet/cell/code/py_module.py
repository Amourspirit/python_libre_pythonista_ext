from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING, Optional
import ast
import copy
import os
import importlib.util

# import importlib
import types
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.ex.general_error import GeneralError
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lplog import (
        LpLog as LibrePythonistaLog,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules import CodeRules
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils import str_util

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.ex.general_error import GeneralError
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lplog import LpLog as LibrePythonistaLog
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules import CodeRules
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils import str_util

    break_mgr = BreakMgr()
    # break_mgr.add_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.init")
    # break_mgr.add_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.execute_code")

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.PyModule"


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
        "from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper import lp_mod",
        "from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lp_mod import lp",
        "from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper.lplog import StaticLpLog as lp_log, LpLog as LibrePythonistaLog",
        "from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.mod_helper import lp_plot",
        "PY_ARGS = None",
        "CURRENT_CELL_OBJ = None",
        "CURRENT_CELL_ID = ''",
        "DUMMY_LAST_VALUE = None",
    ]
    lines = pre_lines + code_lines + post_lines
    return "\n".join(lines)


class PyModule(LogMixin, PyModuleT):
    """
    Singleton Class. Manages the state and execution of Python code within a LibreOffice document.
    """

    def __new__(cls) -> PyModule:
        gbl_cache = DocGlobals.get_current()
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        break_mgr.check_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.init")
        self._is_py_test_running = is_pytest_running()

        self.mod = types.ModuleType("PyMod")
        self._cr = CodeRules()

        # _private_enabled should default to True.
        # If this is to be added as a setting it must be at the document level.
        # This way when a document is shared the setting is also shared.
        self._private_enabled = True

        self._current_ast_mod = None
        self._current_match_rule = None  # used for testing
        self._init_mod()
        self._is_init = True

    def _init_mod(self) -> None:
        self.log.debug("_init_mod()")
        code = get_module_init_code()
        try:
            self._execute_init_code(code, self.mod.__dict__)
            self._init_dict = self.mod.__dict__.copy()
            if lp_plot is not None:
                self._init_dict.update(**lp_plot.__dict__.copy())
            else:
                self.log.warning("lp_plot module is not available.")
            self.log.debug("_init_mod() done.")
        except Exception:
            self.log.exception("Error initializing module")
            raise

    def copy_dict(self) -> Dict[str, Any]:
        """Returns a copy of the module dictionary."""
        return self.mod.__dict__.copy()

    def _execute_init_code(self, code_snippet: str, globals_dict: Optional[dict] = None) -> Any:  # noqa: ANN401
        """
        Compiles and executes the given code snippet.
        - If the last statement is an expression, returns its value.
        - Otherwise, returns the value of `result` if it exists in local variables.
        """

        try:
            if globals_dict is None:
                globals_dict = {}
            globals_dict["_"] = None
            locals = {}

            # Parse the code as a full module
            tree = ast.parse(code_snippet, mode="exec")

            module_body = ast.fix_missing_locations(ast.Module(body=tree.body, type_ignores=[]))
            exec_code = compile(module_body, "<string>", "exec")

            # Execute statements
            # do not use locals here or the module values will be assigned to locals
            # exec(exec_code, globals, locals)
            exec(exec_code, globals_dict)

            # If there was a final expression node, evaluate it

        except SyntaxError as e:
            self.log.exception("Syntax error executing code: \n%s", code_snippet)
            return None

        except Exception as e:
            self.log.exception("Error executing  error: '%s' code: \n%s", e, code_snippet)
            # traceback.print_exc()
            return None

    def execute_code(self, code_snippet: str, globals_dict: Optional[dict] = None) -> Any:  # noqa: ANN401
        """
        Compiles and executes the given code snippet.
        - If the last statement is an expression, returns its value.
        - Otherwise, returns the value of `result` if it exists in local variables.
        """
        if self._is_init:
            break_mgr.check_breakpoint("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.execute_code")

        try:
            if globals_dict is None:
                globals_dict = {}
            globals_dict["_"] = None

            # Parse the code as a full module
            tree = ast.parse(code_snippet, mode="exec")
            # Transform AST so underscore-assignments become local assigns
            # tree = UnderscoreLocalTransformer().visit(tree)
            # ast.fix_missing_locations(tree)
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
            local_dict = {}
            exec(exec_code, globals_dict, local_dict)

            if self._private_enabled:
                filtered_dict = {k: v for k, v in local_dict.items() if not k.startswith("_")}
            else:
                filtered_dict = local_dict

            # If there was a final expression node, evaluate it

            if last_expr:
                expr = ast.Expression(last_expr.value)
                expr = ast.fix_missing_locations(expr)
                eval_code = compile(expr, "<string>", "eval")
                result = eval(eval_code, globals_dict, local_dict)
                if assign_name:
                    if self._private_enabled:
                        if not assign_name.startswith("_"):
                            filtered_dict[assign_name] = result
                    else:
                        filtered_dict[assign_name] = result
                filtered_dict["_"] = result

            globals_dict.update(filtered_dict)

            # If there's no final expression, fallback to returning locals["_"], if present
            return globals_dict.get("_")

        except SyntaxError as e:
            self.log.exception("Syntax error executing code: \n%s", code_snippet)
            return None

        except Exception as e:
            self.log.exception("Error executing  error: '%s' code: \n%s", e, code_snippet)
            # traceback.print_exc()
            return None

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
        self.log.debug("update_with_result() Entered.")
        # try:
        #     code = str_util.remove_comments(code)
        #     code = str_util.clean_string(code)
        #     # self._log.debug(f"Cleaned code. \n{code}")
        # except Exception:
        #     self.log.exception("Error cleaning code: %s", code)
        #     raise

        result = None
        self._current_match_rule = None  # used for testing
        try:
            if code:
                self.log.debug("Executing code.")
                self.execute_code(code, self.mod.__dict__)
                self.log.debug("Executed code.")
            rule = self._cr.get_matched_rule(self.mod, code, self._current_ast_mod)
            self.log.debug("Got matched rule.")
            result = rule.get_value()
            self.log.debug("Got result.")

            if self._is_py_test_running:
                self._current_match_rule = rule
            else:
                # only reset rule if not testing.
                # The _current_match_rule will contain the last matched rule so do reset it.
                rule.reset()
            self.log.debug("Reset rule.")
            return result
        # other exceptions can be caught and new error classes can be created.
        except Exception as e:
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
                    self.log.error("LibrePythonistaLog error", exc_info=True)
                if self.log.is_debug:
                    self.log.warning("Error updating module. Result set to %s.\n%s\n", result, code, exc_info=True)
                else:
                    self.log.warning("Error updating module. Result set to %s.\n", result, exc_info=True)
            except Exception:
                self.log.exception("update_with_result() Error updating module.\n%s\n", code)
                raise
        return result

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        """
        Set a global variable in the module.

        Args:
            var_name (str): The name of the variable
            value (Any): The value of the variable
        """
        self.log.debug("set_global_var(%s, %s)", var_name, value)
        if var_name == "CURRENT_CELL_OBJ":
            self.mod.__dict__["lp_mod"].CURRENT_CELL_OBJ = value
            self.mod.__dict__[var_name] = value
            return
        self.mod.__dict__[var_name] = value
        self.mod.__dict__["_"] = value

    def reset_to_dict(self, mod_dict: Dict[str, Any], code: str = "") -> Any:  # noqa: ANN401
        """
        Reset the module to the given dictionary and returns the last variable in the module if code is present.

        Args:
            mod_dict (dict): A dictionary of variables to reset the module to.
            code (str, optional): Any valid python code

        Returns:
            Any: If there is code the last variable in the module if any; Otherwise, None.
        """

        self.log.debug("reset_to_dict()")
        self.mod.__dict__.clear()
        self.mod.__dict__.update(mod_dict)
        self._current_ast_mod = None
        if not code:
            return None
        code = str_util.remove_comments(code)
        code = str_util.clean_string(code)
        if code:
            self._execute_init_code(code, self.mod.__dict__)
        else:
            return None
        rule = self._cr.get_matched_rule(self.mod, code, self._current_ast_mod)
        result = rule.get_value()
        rule.reset()
        self.log.debug("reset_to_dict() done.")
        return result

    def reset_module(self) -> None:
        """Reset the module to its initial state."""
        self.log.debug("reset_module()")
        self.mod.__dict__.clear()
        self.mod.__dict__.update(self._init_dict)
        self._current_ast_mod = None
        with self.log.indent(True):
            self.log.debug("reset_module() done.")
