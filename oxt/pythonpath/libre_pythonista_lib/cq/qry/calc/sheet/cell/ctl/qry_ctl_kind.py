from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import (
        QryCtlKind as QryPropCtlKind,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind as QryPropCtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.result import Result


class QryCtlKind(QryBase, QryCellT[Union[Result[CtlKind, None], Result[None, Exception]]]):
    """
    Query to determine the control kind (CtlKind) of a cell.

    Args:
        cell (CalcCell): The cell to query
        ctl (Ctl, None): Optional control object to update with query results
    """

    def __init__(self, cell: CalcCell, ctl: Optional[Ctl] = None) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl

    def _qry_prop_kind(self) -> Union[Result[CtlKind, None], Result[None, Exception]]:
        """
        Queries the cell's control kind using QryPropCtlKind.

        Returns:
            Result: Success with CtlKind or Failure with Exception
        """
        qry = QryPropCtlKind(cell=self._cell)
        return self._execute_qry(qry)

    def execute(self) -> Union[Result[CtlKind, None], Result[None, Exception]]:
        """
        Executes the query to get the control kind.
        If a control object was provided, updates it with the results.

        Returns:
            Result: Success with CtlKind or Failure with Exception
        """
        kind = self._qry_prop_kind()
        if Result.is_failure(kind):
            return kind
        if self._ctl is not None:
            self._ctl.control_kind = kind.data
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return kind

    @property
    def cell(self) -> CalcCell:
        """The cell being queried"""
        return self._cell
