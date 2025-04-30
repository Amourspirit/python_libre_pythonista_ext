from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule


def test_plot_expr(py_mod: PyModule, mocker: MockerFixture) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr import LpFnPlotExpr
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr import LpFnPlotExpr

    py_mod.mod.__dict__["plt"] = mocker.MagicMock()
    py_mod.mod.__dict__["lp_plot"] = mocker.MagicMock()

    py_mod.mod.plt.show = mocker.MagicMock()
    py_mod.mod.plt.show.return_value = None
    py_mod.mod.__dict__["lp_plot"].LAST_LP_RESULT = DotDict(
        data="/tmp/file.svg", file_kind="image", file_ext="svg", details="figure"
    )
    code = """
plt.show()
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnPlotExpr)
    assert result is not None
    assert result.data == "/tmp/file.svg"
    assert result.file_kind == "image"
    assert result.file_ext == "svg"
    assert result.details == "figure"


def test_plot_assign(py_mod: PyModule, mocker: MockerFixture) -> None:
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign import (
            LpFnPlotAssign,
        )
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign import LpFnPlotAssign

    py_mod.mod.__dict__["plt"] = mocker.MagicMock()
    py_mod.mod.__dict__["lp_plot"] = mocker.MagicMock()

    py_mod.mod.plt.show = mocker.MagicMock()
    py_mod.mod.plt.show.return_value = None
    py_mod.mod.__dict__["lp_plot"].LAST_LP_RESULT = DotDict(
        data="/tmp/file.svg", file_kind="image", file_ext="svg", details="figure"
    )
    code = """
_ = plt.show()
"""

    result = py_mod.update_with_result(code)
    assert isinstance(py_mod._current_match_rule, LpFnPlotAssign)
    assert result is not None
    assert result.data == "/tmp/file.svg"
    assert result.file_kind == "image"
    assert result.file_ext == "svg"
    assert result.details == "figure"
