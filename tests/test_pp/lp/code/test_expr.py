from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from .....build.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule


def test_sum_it(py_mod: PyModule) -> None:
    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.expr import Expr
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.expr import Expr
    code = """
def sum_it(a: int, b: int) -> int:
    return a + b

sum_it(1, 2)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Expr)
    assert result is not None
    assert result.data == 3

    code = "10 * 2"

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Expr)
    assert result is not None
    assert result.data == 20

    code = "'hello'"

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Expr)
    assert result is not None
    assert result.data == "hello"

    code = '"""Bob\nis\nyour\nuncle"""'

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Expr)
    assert result is not None
    assert result.data == "Bob\nis\nyour\nuncle"
