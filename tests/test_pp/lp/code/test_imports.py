from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_import_py_module(loader, build_setup, mocker: MockerFixture) -> None:  # noqa: ANN001
    from ooodev.calc import CalcDoc

    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_obj.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_value.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules.BreakMgr")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.BreakMgr")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.LibrePythonistaLog")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        inst = PyModule()
        assert inst is not None
    finally:
        if doc is not None:
            doc.close(True)
