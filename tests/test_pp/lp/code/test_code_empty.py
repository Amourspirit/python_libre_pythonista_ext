from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from .....build.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule


def test_code_empty(py_mod: PyModule, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_empty import CodeEmpty
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_empty import CodeEmpty

    result = py_mod.update_with_result("")
    assert isinstance(py_mod._current_match_rule, CodeEmpty)
    assert result is not None
    assert not result.data
