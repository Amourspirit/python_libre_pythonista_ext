from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


# build_setup


def test_expr(
    build_setup,
    mocker: MockerFixture,
) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.expr import Expr
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.expr import Expr

    inst = Expr()
    assert inst is not None

    # from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule


def test_code_empty(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_empty import CodeEmpty
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_empty import CodeEmpty

    inst = CodeEmpty()
    assert inst is not None


def test_assign(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.assign import Assign
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.assign import Assign

    inst = Assign()
    assert inst is not None


def test_last_dict(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.underscore import Underscore
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.underscore import Underscore

    inst = Underscore()
    assert inst is not None


def test_lp_fn_assign(build_setup, mocker: MockerFixture) -> None:
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign.LogInst")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign import LpFnAssign
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign import LpFnAssign

    inst = LpFnAssign()
    assert inst is not None


def test_lp_fn_expr(build_setup, mocker: MockerFixture) -> None:
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr.LogInst")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr import LpFnExpr
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr import LpFnExpr

    inst = LpFnExpr()
    assert inst is not None


def test_lp_fn_plot_assign(build_setup, mocker: MockerFixture) -> None:
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign import (
            LpFnPlotAssign,
        )
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign import LpFnPlotAssign

    inst = LpFnPlotAssign()
    assert inst is not None


def test_lp_fn_plot_expr(build_setup, mocker: MockerFixture) -> None:
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr import LpFnPlotExpr
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr import LpFnPlotExpr

    inst = LpFnPlotExpr()
    assert inst is not None


def test_import_code_rules(build_setup, mocker: MockerFixture) -> None:
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules.BreakMgr")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules import CodeRules
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules import CodeRules

    inst = CodeRules()
    assert inst is not None
