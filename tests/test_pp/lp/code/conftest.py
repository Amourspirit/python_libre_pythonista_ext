from __future__ import annotations
from typing import TYPE_CHECKING
from pytest_mock import MockerFixture

import pytest


@pytest.fixture(scope="function")
def py_mod(build_setup, mocker: MockerFixture):  # noqa: ANN001, ANN201
    # _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_obj.LogInst")
    _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_plot_expr.LogInst")
    _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_plot_assign.LogInst")
    # _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_value.LogInst")
    # _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn.LogInst")
    _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_assign.LogInst")
    _ = mocker.patch("libre_pythonista_lib.code.rules.lp_fn_expr.LogInst")

    # _ = mocker.patch("libre_pythonista_lib.code.rules.code_rules.LogInst")
    _ = mocker.patch("libre_pythonista_lib.code.rules.code_rules.OxtLogger")
    _ = mocker.patch("libre_pythonista_lib.code.rules.code_rules.BreakMgr")

    _ = mocker.patch("libre_pythonista_lib.code.py_module.OxtLogger")
    _ = mocker.patch("libre_pythonista_lib.code.py_module.BreakMgr")
    _ = mocker.patch("libre_pythonista_lib.code.py_module.LibrePythonistaLog")

    if TYPE_CHECKING:
        from .....build.pythonpath.libre_pythonista_lib.code.py_module import PyModule
    else:
        from libre_pythonista_lib.code.py_module import PyModule

    inst = PyModule()
    assert inst is not None
    return inst
