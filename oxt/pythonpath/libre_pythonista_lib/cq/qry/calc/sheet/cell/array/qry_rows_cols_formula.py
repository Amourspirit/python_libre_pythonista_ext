from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING

from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryRowsColsFormula(QryBase, LogMixin, QryCellT[Result[List[int], None] | Result[None, Exception]]):
    """
    Query that returns the number of rows and columns represented by the cell Formula array

    Args:
        cell (CalcCell): The cell to query
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the query with a cell and optional module.

        Args:
            cell (CalcCell): The cell to query
            mod (PyModuleT | None, optional): Optional Python module. If None, will be queried using QryPyModuleDefault. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_formula_range(self) -> RangeObj:
        qry = QryFormulaRange(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def execute(self) -> Result[List[int], None] | Result[None, Exception]:
        """
        Executes the query to get Formula Array dimensions.

        Returns:
            Result: Success with [num_rows, num_cols] or Failure with Exception
        """

        try:
            rng = self._qry_formula_range()
            result = [rng.row_count, rng.col_count]
            return Result.success(result)
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """The cell being queried"""
        return self._cell
