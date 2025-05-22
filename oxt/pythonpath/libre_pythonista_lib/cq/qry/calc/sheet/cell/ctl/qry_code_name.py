from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import (
        QryCodeName as QryPropCodeName,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName as QryPropCodeName
    from libre_pythonista_lib.utils.result import Result


class QryCodeName(QryBase, QryCellT[Union[Result[str, None], Result[None, Exception]]]):
    """Gets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Optional[Ctl] = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl

    def execute(self) -> Union[Result[str, None], Result[None, Exception]]:
        """
        Executes the query to get code name

        Returns:
            Result: Success with code name or Failure with Exception
        """
        qry_code_name = QryPropCodeName(cell=self.cell)
        qry_result = self._execute_qry(qry_code_name)
        if Result.is_failure(qry_result):
            return qry_result

        if self._ctl is not None:
            self._ctl.ctl_code_name = qry_result.data
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return qry_result

    @property
    def cell(self) -> CalcCell:
        return self._cell
