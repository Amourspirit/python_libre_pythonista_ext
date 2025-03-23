from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_is_pyc_formula(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import (
            QryCellIsPycFormula,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import QryCellIsPycFormula
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.const import FORMULA_PYC

    handler = QryHandler()

    # Mock SheetCell
    mock_cell = mocker.MagicMock()

    # Test case 1: Cell is deleted
    mock_is_deleted = mocker.patch(
        "libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted.QryCellIsDeleted.execute",
        return_value=True,
    )
    qry = QryCellIsPycFormula(cell=mock_cell)
    assert handler.handle(qry) is False
    mock_is_deleted.assert_called_once()

    # Test case 2: Empty formula
    mock_is_deleted.return_value = False
    mock_cell.getFormula.return_value = ""
    assert handler.handle(qry) is False

    # Test case 3: Regular formula (not PYC)
    mock_cell.getFormula.return_value = "=A1+B1"
    assert handler.handle(qry) is False

    # Test case 4: PYC formula
    mock_cell.getFormula.return_value = f'={FORMULA_PYC}(SHEET(),CELL("ADDRESS"))'
    assert handler.handle(qry) is True

    # Test case 5: Exception handling
    mock_cell.getFormula.side_effect = Exception("Test error")
    assert handler.handle(qry) is False


def test_cell_is_pyc_formula_properties(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import (
            QryCellIsPycFormula,
        )
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import QryCellIsPycFormula
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    # Mock SheetCell
    mock_cell = mocker.MagicMock()

    qry = QryCellIsPycFormula(cell=mock_cell)

    # Test cell property
    assert qry.cell == mock_cell

    # Test kind property
    assert qry.kind == CalcQryKind.SIMPLE

    # Test kind setter
    qry.kind = CalcQryKind.CELL
    assert qry.kind == CalcQryKind.CELL
