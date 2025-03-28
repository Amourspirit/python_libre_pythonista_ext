from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.calc import CalcSheet, SpreadsheetDrawPage
from ooodev.draw.shapes import DrawShape

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape as QryShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape as QryShapeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryLpShape(
    QryBase, LogMixin, QryCellT[Result[DrawShape[SpreadsheetDrawPage[CalcSheet]], None] | Result[None, Exception]]
):
    """Gets the control shape"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self.kind = CalcQryKind.CELL
        self._ctl = ctl

    def _get_shape_name(self) -> Result[str, None] | Result[None, Exception]:
        qry_shape = QryShapeName(cell=self.cell)
        return self._execute_qry(qry_shape)

    def execute(self) -> Result[DrawShape[SpreadsheetDrawPage[CalcSheet]], None] | Result[None, Exception]:
        """
        Executes the query to get control shape

        Returns:
            Result: Success with shape or Failure with Exception
        """
        qry_shape_name = QryShapeName(cell=self.cell)
        result = self._execute_qry(qry_shape_name)
        if Result.is_failure(result):
            return result

        try:
            shape_name = result.data
            qry_shape = QryShapeByName(sheet=self.cell.calc_sheet, shape_name=shape_name)
            qry_result = self._execute_qry(qry_shape)
            if Result.is_failure(qry_result):
                return qry_result
            result = qry_result.data
            self.log.debug("Found shape for : %s", shape_name)
            if self._ctl is not None:
                self._ctl.ctl_shape = result
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            return Result.success(result)
        except Exception:
            self.log.exception("Error getting shape")
            return Result.failure(Exception("Shape not found"))

    @property
    def cell(self) -> CalcCell:
        return self._cell
