from __future__ import annotations
from typing import TYPE_CHECKING, Any
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

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        manager = PySourceManager(doc)
        yield manager
    finally:
        if doc is not None:
            doc.close(True)


def test_add_source(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    # Test adding source code to a cell
    code = "x = 42\nprint(x)"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)

    py_source_manager.add_source(code, cell_obj)
    py_src = py_source_manager[cell_obj]
    assert py_src.dd_data.data is None

    # Verify source was added
    assert cell_obj in py_source_manager
    assert py_source_manager[cell_obj].source_code == code


def test_update_source(py_source_manager: PySourceManager) -> None:
    from ooodev.utils.data_type.cell_obj import CellObj

    # First add source
    initial_code = "x = 42"
    cell_obj = CellObj.from_idx(col_idx=0, row_idx=0, sheet_idx=0)
    py_source_manager.add_source(initial_code, cell_obj)
    py_src = py_source_manager[cell_obj]
    assert py_src.dd_data.data == 42

    # Update the source
    updated_code = "x = 100"
    py_source_manager.update_source(updated_code, cell_obj)

    # Verify source was updated
    assert py_source_manager[cell_obj].source_code == updated_code
    assert py_src.dd_data.data == 100


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
    py_src1 = py_source_manager[cell1]
    assert py_src1.dd_data.data == 42
    py_source_manager.add_source("y = x + 10", cell2)
    py_src2 = py_source_manager[cell2]
    assert py_src2.dd_data.data == 52

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
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager  # type: ignore

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)

        # Create two instances with same doc
        manager1 = PySourceManager(doc)
        manager2 = PySourceManager(doc)

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
