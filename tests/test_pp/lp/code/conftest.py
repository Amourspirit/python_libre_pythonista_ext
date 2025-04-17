from __future__ import annotations
from typing import TYPE_CHECKING
from pytest_mock import MockerFixture

import pytest


@pytest.fixture(scope="function")
def py_mod(loader, build_setup, mocker: MockerFixture):  # noqa: ANN001, ANN201
    from ooodev.calc import CalcDoc

    # _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_obj.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_expr.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_plot_assign.LogInst")
    # _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_value.LogInst")
    # _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.lp_fn_expr.LogInst")

    # _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules.LogInst")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.rules.code_rules.BreakMgr")

    # _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.OxtLogger")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.BreakMgr")
    _ = mocker.patch("libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module.LibrePythonistaLog")

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule

    doc = CalcDoc.create_doc(loader=loader)

    inst = PyModule()
    assert inst is not None
    yield inst
    doc.close(True)
