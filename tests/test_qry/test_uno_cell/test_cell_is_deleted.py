from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture
from com.sun.star.uno import RuntimeException

if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_is_deleted(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    else:
        from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.query.qry_handler import QryHandler

    handler = QryHandler()

    # Mock SheetCell
    mock_cell = mocker.Mock()

    # Test non-deleted cell
    type(mock_cell).AbsoluteName = mocker.PropertyMock(return_value="Sheet1.A1")
    qry = QryCellIsDeleted(cell=mock_cell)
    assert qry.kind == CalcQryKind.SIMPLE
    assert qry.cell == mock_cell
    assert handler.handle(qry) is False

    # Test RuntimeException case - cell deleted
    # Test deleted cell
    type(mock_cell).AbsoluteName = mocker.PropertyMock(side_effect=RuntimeException())
    qry = QryCellIsDeleted(cell=mock_cell)
    assert handler.handle(qry) is True

    # Test kind property setter
    qry.kind = CalcQryKind.CELL
    assert qry.kind == CalcQryKind.CELL
