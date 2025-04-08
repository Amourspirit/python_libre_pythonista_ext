from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState as QryPropState
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols import QryRowCols
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState as QryPropState
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols import QryRowCols
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange
    from libre_pythonista_lib.utils.result import Result


class QryIsUpdateRequired(QryBase, LogMixin, QryCellT[bool]):
    """
    Checks if the cell needs an update.

    If the cell is not an array formula, then an update is not needed.
    If the cell is not expanded as a array formula, then an update is not needed.
    If the cell is an array formula, then an update is needed if the data range has changed.

    Returns:
        bool: True if the cell needs an update.
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the query.

        Args:
            cell (CalcCell): The cell to check for required updates.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_state(self) -> StateKind:
        """
        Query the state of the cell.

        Returns:
            StateKind: The state of the cell (e.g., ARRAY, UNKNOWN).
        """
        qry = QryPropState(cell=self.cell)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return StateKind.UNKNOWN

    def _qry_rows_cols(self) -> Tuple[int, ...]:
        """
        Query the number of rows and columns in the cell array.

        Returns:
            Tuple[int, ...]: A tuple containing the row and column counts.

        Raises:
            Exception: If the query fails.
        """
        qry = QryRowCols(cell=self.cell)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return tuple(qry_result.data)
        raise qry_result.error

    def _qry_formula_range(self) -> RangeObj:
        """
        Query the range of the formula in the cell.

        Returns:
            RangeObj: The range object representing the formula's range.

        Raises:
            Exception: If the query fails.
        """
        qry = QryFormulaRange(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def execute(self) -> bool:
        """
        Execute the query to determine if the cell needs an update.

        Returns:
            bool: True if the cell needs an update, False otherwise.
        """
        try:
            state = self._qry_state()
            if state != StateKind.ARRAY:
                return False
            rows_cols = self._qry_rows_cols()
            rng = self._qry_formula_range()
            result = bool(rng.row_count != rows_cols[0] or rng.col_count != rows_cols[1])
            self.log.debug("Cell %s formula update required is: %s", self.cell.cell_obj, result)
            return result

        except Exception as e:
            self.log.exception("Error executing query: %s", e)
        return False

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell being queried.

        Returns:
            CalcCell: The cell instance.
        """
        return self._cell
