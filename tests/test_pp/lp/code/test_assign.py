from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from .....build.pythonpath.libre_pythonista_lib.code.py_module import PyModule


def test_sum_it(py_mod: PyModule, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.rules.assign import Assign
    else:
        from libre_pythonista_lib.code.rules.assign import Assign
    code = """
def sum_it(a: int, b: int) -> int:
    return a + b

result = sum_it(1, 2)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 3

    code = """
def multi_it(
    a: int,
    b: int
) -> int:
    return a * b

result = multi_it(2, 3)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 6

    code = """
def multi2_it(
    a: int,
    b: int
) -> int:
    return a * b

result:int = multi_it(2, 3)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 6

    code = """
def add_it(a: int, b: int) -> int:
    return a + b
"""
    result = py_mod.update_with_result(code)
    assert py_mod._current_match_rule is not None


def test_underscore(py_mod: PyModule, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.rules.assign import Assign
    else:
        from libre_pythonista_lib.code.rules.assign import Assign
    code = """
_x = 1
def sum_it(a: int, b: int) -> int:
    return a + b

result = sum_it(_x, 2)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 3
    assert "_x" not in py_mod.mod.__dict__
    assert "sum_it" in py_mod.mod.__dict__
    assert "result" in py_mod.mod.__dict__

    code = """
_y = 5
def _sum_it(a: int, b: int) -> int:
    return a + b

result = _sum_it(_y, 5)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 10
    assert "_y" not in py_mod.mod.__dict__
    assert "_sum_it" not in py_mod.mod.__dict__
    assert "result" in py_mod.mod.__dict__

    code = """
_z = 2
def _add_it(a: int, b: int) -> int:
    return a + b

_result = _add_it(_z, 5)
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, Assign)
    assert result is not None
    assert result.data == 7
    assert "_z" not in py_mod.mod.__dict__
    assert "_add_it" not in py_mod.mod.__dict__
    assert "_result" not in py_mod.mod.__dict__
