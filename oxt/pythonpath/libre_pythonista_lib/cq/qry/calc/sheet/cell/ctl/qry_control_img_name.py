from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import (
        QryCodeName as QryPropCodeName,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName as QryPropCodeName
    from libre_pythonista_lib.utils.result import Result


class QryControlImgName(QryBase, QryCellT[Result[str, None] | Result[None, Exception]]):
    """Gets the control name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl

    def _qry_control_name(self, code_name: str) -> str:
        """Gets the control name such as ``libre_pythonista_cell_id_S4JaB6LmJGR2HU``"""
        qry = QryShapeNameImg(code_name=code_name)
        return self._execute_qry(qry)

    def execute(self) -> Result[str, None] | Result[None, Exception]:
        """
        Executes the query to get control name

        Returns:
            Result: Success with control name or Failure with Exception
        """
        if self._ctl is not None and self._ctl.ctl_code_name:
            control_name = self._qry_control_name(self._ctl.ctl_code_name)
        else:
            control_name = ""

        if not control_name:
            qry_code_name = QryPropCodeName(cell=self.cell)
            qry_result = self._execute_qry(qry_code_name)
            if Result.is_failure(qry_result):
                return qry_result
            control_name = self._qry_control_name(qry_result.data)

        if not control_name:
            return Result.failure(Exception("Control name not found"))

        if self._ctl is not None:
            self._ctl.ctl_name = control_name
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return Result.success(control_name)

    @property
    def cell(self) -> CalcCell:
        return self._cell
