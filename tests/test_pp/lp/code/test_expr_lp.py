from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from .....build.pythonpath.libre_pythonista_lib.code.py_module import PyModule


def test_lp_cell(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr
    else:
        from libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr

    def lp(x, headers=False) -> int:  # noqa: ANN001
        return 2

    py_mod.mod.__dict__["lp"] = lambda x: 2

    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=2)
    code = """
lp("A1")
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 2

    code = """
lp(
    "A1"
)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 2


def test_lp_range(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr
    else:
        from libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr

    py_mod.mod.__dict__["lp"] = lambda x: 3
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=3, headers=False)
    code = """
lp("A1:C3")
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 3

    code = """
lp(
    "A1:C3"
)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 3


def test_lp_range_headers(py_mod: PyModule) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr
    else:
        from libre_pythonista_lib.code.rules.lp_fn_expr import LpFnExpr

    def lp(x, headers=False) -> int:  # noqa: ANN001
        return 4

    py_mod.mod.__dict__["lp"] = lp
    py_mod.mod.lp_mod.LAST_LP_RESULT = DotDict(data=4, headers=False)
    code = """
lp("A1:C3", headers=True)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 4

    code = """

# this is a comment
lp(
    "A1:C3", # noqa: ANN001
    headers=True
)
# another comment
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnExpr)
    assert result is not None
    assert result.data == 4
