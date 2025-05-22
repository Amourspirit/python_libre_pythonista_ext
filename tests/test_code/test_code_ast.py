from __future__ import annotations
from typing import Any, cast, Optional
import ast
import types
import importlib.util
# import traceback

import pytest

if __name__ == "__main__":
    pytest.main([__file__])


def is_import_available(module_name: str) -> bool:
    spec = importlib.util.find_spec(module_name)
    return spec is not None


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
        "PY_ARGS = None",
        "CURRENT_CELL_OBJ = None",
        "CURRENT_CELL_ID = ''",
        "DUMMY_LAST_VALUE = None",
    ]
    lines = pre_lines + code_lines + post_lines
    return "\n".join(lines)


def execute_code(code_snippet: str, globals: Optional[dict] = None, _private_enabled: bool = True) -> Any:  # noqa: ANN401
    """
    Compiles and executes the given code snippet.
    - If the last statement is an expression, returns its value.
    - Otherwise, returns the value of `result` if it exists in local variables.
    """

    # _private should default to True.
    # If thi is to be added as a setting it must be at the document level.
    # This way when a document is shared the setting is also shared.
    # If this were a setting, it would have to be on the document level.

    try:
        if globals is None:
            globals = {}
        globals["_"] = None
        locals = {}

        # Parse the code as a full module
        tree = ast.parse(code_snippet, mode="exec")

        # If the last node is an expression, remove it for separate handling
        last_expr = None
        assign_name = ""
        # print(str(type(tree.body[-1])))
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_expr = cast(ast.Expr, tree.body.pop())
        elif tree.body and isinstance(tree.body[-1], ast.Assign):
            last_expr = cast(ast.Assign, tree.body.pop())
            try:
                assign_name = last_expr.targets[0].id  # type: ignore
            except Exception:
                assign_name = ""

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
                if _private_enabled:
                    if not assign_name.startswith("_"):
                        globals[assign_name] = result
                else:
                    globals[assign_name] = result
            globals["_"] = result

        # If there's no final expression, fallback to returning locals["_"], if present
        return globals.get("_")

    except Exception:
        # traceback.print_exc()
        return None


class PyModule:
    def __init__(self) -> None:
        self.mod = types.ModuleType("PyMod")
        self._init_mod()

    def _init_mod(self) -> None:
        code = get_module_init_code()
        # from .mod_fn import lp
        try:
            # t = threading.Thread(target=exec, args=(code, self.mod.__dict__), daemon=True)
            # t.start()
            # t.join()
            # exec(code, self.mod.__dict__)
            execute_code(code, globals=self.mod.__dict__)
            # setattr(self.mod, "lp", lp.lp)
            self._init_dict = self.mod.__dict__.copy()
            if lp_plot is not None:
                self._init_dict.update(**lp_plot.__dict__.copy())

        except Exception:
            raise


def test_assign_to_var() -> None:
    code_snippet = """

first = 'Hello'
last = 'World'
def concat(a, b):
    return a + ' ' + b
result = concat(first, last)

"""
    res = execute_code(code_snippet)
    assert res == "Hello World"


def test_assign_fn() -> None:
    code_snippet = """
x = 10
y = 20
def addit(a, b):
    return a + b
addit(x, y)


"""
    res = execute_code(code_snippet)
    assert res == 30


def test_assign_fn_comments() -> None:
    code_snippet = """
# Add x and y
x = 10
y = 20
def addit(a, b):
    # Add a and b
    return a + b
addit(x, y)

# not more comments
"""
    res = execute_code(code_snippet)
    assert res == 30


def test_no_assign() -> None:
    code_snippet = """
# Add x and y
x = 10
y = 20
def addit(a, b):
    # Add a and b
    return a + b

# not more comments
"""
    res = execute_code(code_snippet)
    assert res is None


def test_class() -> None:
    code_snippet = """
# Add x and y

class Adder:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self):
        return self.a + self.b

adder = Adder(10, 20)
adder.add()
        
# not more comments
"""
    res = execute_code(code_snippet)
    assert res == 30


def test_class_mod_init() -> None:
    code_init = get_module_init_code()
    code_snippet = """
# Add x and y

class Adder:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self):
        return self.a + self.b

adder = Adder(10, 20)
adder.add()
        
# not more comments
"""
    res = execute_code(code_init + code_snippet)
    assert res == 30


def test_pandas_dataframe(import_available) -> None:  # noqa: ANN001
    if not import_available("pandas"):
        pytest.skip("Skipping this test because pandas in not installed.")
    code_init = get_module_init_code()
    code_snippet = """
import pandas as pd
data = {'x': [1, 2, 3, 4, 5], 'y': [10, 20, 25, 30, 35]}
df = pd.DataFrame(data)
"""
    res = execute_code(code_init + code_snippet)
    assert res is not None
    assert type(res).__name__ == "DataFrame"


def test_pandas_series(import_available) -> None:  # noqa: ANN001
    if not import_available("pandas"):
        pytest.skip("Skipping this test because pandas in not installed.")
    code_init = get_module_init_code()
    code_snippet = """
import pandas as pd
data = {'x': [1, 2, 3, 4, 5], 'y': [10, 20, 25, 30, 35]}
df = pd.DataFrame(data)
s = df['x']
"""
    res = execute_code(code_init + code_snippet)
    assert res is not None
    assert type(res).__name__ == "Series"


def test_reassign_to_var() -> None:
    py_mod = PyModule()

    code_snippet = """

first = 'Hello'
last = 'World'
def concat(a, b):
    return a + ' ' + b
result = concat(first, last)

"""
    res = execute_code(code_snippet, globals=py_mod.mod.__dict__)
    assert res == "Hello World"
    assert py_mod.mod.__dict__["result"] == "Hello World"

    code_snippet = "result = 'done'"
    res = execute_code(code_snippet, globals=py_mod.mod.__dict__)
    assert res == "done"
    assert py_mod.mod.__dict__["result"] == "done"
    assert "DUMMY_LAST_VALUE" in py_mod.mod.__dict__


def test_private_var() -> None:
    py_mod = PyModule()

    code_snippet = """

first = 'Hello'
last = 'World'
def concat(a, b):
    return a + ' ' + b
_result = concat(first, last)

"""
    res = execute_code(code_snippet, globals=py_mod.mod.__dict__, _private_enabled=True)
    assert res == "Hello World"
    assert "_result" not in py_mod.mod.__dict__
