from __future__ import annotations
from typing import cast, TYPE_CHECKING, Any
import pytest
from pytest_mock import MockerFixture

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from ooodev.utils.data_type.cell_obj import CellObj


@pytest.fixture
def py_source_manager(loader, build_setup) -> Any:
    from ooodev.calc import CalcDoc
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager  # type: ignore
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule  # type: ignore

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        manager = PySourceManager(doc=doc, mod=PyModule())
        yield manager
    finally:
        if doc is not None:
            doc.close(True)


def test_add_source(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import (
            QryModuleStateLastItem,
        )
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
        from libre_pythonista_lib.utils.result import Result
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import QryModuleStateLastItem

    # Test adding source code to a cell
    qry_handler = QryHandlerFactory.get_qry_handler()
    code = "x = 42\nprint(x)"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)

    py_source_manager.add_source(code, cell_obj)
    # py_src = py_source_manager[cell_obj]
    qry = QryModuleStateLastItem(py_source_manager.mod)
    state = qry_handler.handle(qry)
    assert Result.is_success(state)
    assert state.data.cell_obj == cell_obj
    assert state.data.dd_data.data is None

    # Verify source was added
    assert cell_obj in py_source_manager
    assert py_source_manager[cell_obj].source_code == code


def test_update_source(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import (
            QryModuleStateLastItem,
        )
    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state_last_item import QryModuleStateLastItem

    # First add source
    initial_code = "x = 42"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
    py_source_manager.add_source(initial_code, cell_obj)
    state = py_source_manager.qry_last_module_state_item()
    assert state is not None
    assert state.cell_obj == cell_obj
    assert state.dd_data.data == 42

    # Update the source
    updated_code = "x = 100"
    py_source_manager.update_source(updated_code, cell_obj)

    # Verify source was updated
    assert py_source_manager[cell_obj].source_code == updated_code
    state = py_source_manager.qry_last_module_state_item()
    assert state is not None
    assert state.cell_obj == cell_obj
    assert state.dd_data.data == 100

    cell_obj2 = CellObj.from_idx(col_idx=1, row_idx=0, sheet_idx=0)
    code = "y = 10\nz = x + y"
    py_source_manager.add_source(code, cell_obj2)
    state2 = py_source_manager.qry_last_module_state_item()
    assert state2 is not None
    assert state2.dd_data.data == 110


def test_path_loc(py_source_manager: PySourceManager) -> None:
    from ooodev.loader import Lo
    from ooodev.utils.data_type.cell_obj import CellObj

    if not TYPE_CHECKING:
        from ooodev.calc import CalcDoc  # type: ignore

    doc = cast(CalcDoc, Lo.current_doc)
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
    sheet = doc.sheets[0]
    cell = sheet[cell_obj]

    code = """
from pathlib import Path
str(Path.cwd())
"""

    py_source_manager.add_source(code, cell_obj)

    state_last = py_source_manager.qry_last_module_state_item()
    assert state_last is not None

    data = (
        state_last.dd_data.data
    )  # something like '/home/paul/Documents/Projects/Python/LibreOffice/python_libre_pythonista_ext'
    assert isinstance(data, str)
    assert data != ""

    state = py_source_manager.qry_module_state_item(cell)
    assert state is not None
    assert state == state_last
    assert state.dd_data.data == data


def test_lo_current_cell_obj(py_source_manager: PySourceManager) -> None:
    from ooodev.loader import Lo
    from ooodev.utils.data_type.cell_obj import CellObj
    from ooodev.calc import CalcDoc  # type: ignore

    doc = cast(CalcDoc, Lo.current_doc)
    sheet = doc.sheets[0]
    sheet["A1"].value = 10

    # First add source
    initial_code = "x = 42"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=1, sheet_idx=0)
    cell = sheet[cell_obj]
    py_source_manager.add_source(initial_code, cell_obj)
    py_src = py_source_manager[cell_obj]
    state = py_source_manager.qry_module_state_item(cell)
    assert state is not None
    assert state.cell_obj == cell_obj
    assert state.dd_data.data == 42

    # Update the source
    updated_code = "x = 100"
    py_source_manager.update_source(updated_code, cell_obj)

    # Verify source was updated
    assert py_source_manager[cell_obj].source_code == updated_code
    state = py_source_manager.qry_module_state_item(cell)
    assert state is not None
    assert state.dd_data.data == 100

    cell_obj2 = CellObj.from_idx(col_idx=1, row_idx=1, sheet_idx=0)
    code = "y = 10\nz = x + y"
    py_source_manager.add_source(code, cell_obj2)
    state2 = py_source_manager.qry_last_module_state_item()
    assert state2 is not None
    assert state2.dd_data.data == 110

    cell_obj3 = CellObj.from_idx(col_idx=3, row_idx=1, sheet_idx=0)
    code = """
doc = Lo.current_doc
sheet = doc.sheets[CURRENT_CELL_OBJ.sheet_idx]
cell = sheet["A1"]
cell.value
"""
    py_source_manager.add_source(code, cell_obj3)
    state3 = py_source_manager.qry_last_module_state_item()
    assert state3 is not None
    assert state3.dd_data.data == 10


def test_remove_source(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    # First add source
    code = "x = 42"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
    py_source_manager.add_source(code, cell_obj)

    # Remove the source
    py_source_manager.remove_source(cell_obj)

    # Verify source was removed
    assert cell_obj not in py_source_manager


def test_get_module_source_code(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    # Add multiple sources
    cell1 = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
    cell2 = CellObj.from_idx(col_idx=1, row_idx=0, sheet_idx=0)

    py_source_manager.add_source("x = 42", cell1)
    state1 = py_source_manager.qry_last_module_state_item()
    assert state1 is not None
    assert state1.cell_obj == cell1
    assert state1.dd_data.data == 42

    py_source_manager.add_source("y = x + 10", cell2)
    py_src2 = py_source_manager[cell2]
    state2 = py_source_manager.qry_last_module_state_item()
    assert state2 is not None
    assert state2.cell_obj == cell2
    assert state2.dd_data.data == 52

    # Get complete module source
    source_code = py_source_manager.get_module_source_code()

    # Verify source contains both cells' code
    assert "x = 42" in source_code
    assert "y = x + 10" in source_code

    # Test with max_cell
    partial_source = py_source_manager.get_module_source_code(max_cell=cell1)
    assert "x = 42" in partial_source
    assert "y = x + 10" not in partial_source


def test_singleton_behavior(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.data_type.cell_obj import CellObj

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager  # type: ignore
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule  # type: ignore
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager  # type: ignore
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule  # type: ignore

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        mod = PyModule()

        # Create two instances with same doc
        manager1 = PySourceManager(doc=doc, mod=mod)
        manager2 = PySourceManager(doc=doc, mod=mod)

        # Verify they are the same instance
        assert manager1 is manager2

        # Add source using first instance
        cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
        manager1.add_source("x = 42", cell_obj)

        # Verify source is accessible from second instance
        assert cell_obj in manager2
        assert manager2[cell_obj].source_code == "x = 42"

    finally:
        if doc is not None:
            doc.close(True)
