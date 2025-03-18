from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_module_state_last_item(loader, build_setup, mocker: MockerFixture) -> None:
    """Test QryModuleStateLastItem query"""
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
        from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.code.py_module_state import PyModuleState
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import (
            QryModuleStateLastItem,
        )
    else:
        from libre_pythonista_lib.code.py_module import PyModule
        from libre_pythonista_lib.code.module_state_item import ModuleStateItem
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import QryModuleStateLastItem
        from libre_pythonista_lib.code.py_module_state import PyModuleState

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        qry_handler = QryHandlerFactory.get_qry_handler()
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Create a PyModule instance and add some code to create state
        mod = PyModule()
        state = PyModuleState(mod)
        code = "x = 42"
        state.update_with_result(cell=cell, code=code)

        # Create and execute query
        qry = QryModuleStateLastItem(mod=mod)
        result = qry_handler.handle(qry)

        # Verify result
        assert isinstance(result, ModuleStateItem)
        assert result.dd_data.data == 42

        # Test with empty module
        mod = PyModule()
        qry = QryModuleStateLastItem(mod=mod)
        result = qry_handler.handle(qry)
        assert result is None

    finally:
        if doc is not None:
            doc.close(True)


def test_qry_module_state_last_item_multiple_states(loader, build_setup) -> None:
    """Test QryModuleStateLastItem with multiple state changes"""
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule
        from oxt.pythonpath.libre_pythonista_lib.code.py_module_state import PyModuleState
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import (
            QryModuleStateLastItem,
        )
    else:
        from libre_pythonista_lib.code.py_module import PyModule
        from libre_pythonista_lib.code.py_module_state import PyModuleState
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import QryModuleStateLastItem

    doc = None
    try:
        qry_handler = QryHandlerFactory.get_qry_handler()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        mod = PyModule()
        state = PyModuleState(mod)

        # Add multiple states
        state.update_with_result(cell=cell, code="x = 10")
        state.update_with_result(cell=cell, code="x = 20")
        state.update_with_result(cell=cell, code="x = 30")

        qry = QryModuleStateLastItem(mod=mod)
        result = qry_handler.handle(qry)

        assert result is not None
        assert result.dd_data.data == 30

    finally:
        if doc is not None:
            doc.close(True)
