from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState as QryPropState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState as QryPropState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result


class QryState(QryBase, QryCellT[Result[StateKind, None] | Result[None, Exception]]):
    """Gets the state of the cell"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl

    def _qry_state_prop(self) -> Result[StateKind, None] | Result[None, Exception]:
        """
        Queries the cell's state using QryPropState.

        Returns:
            Result: Success with StateKind or Failure with Exception
        """
        qry = QryPropState(cell=self._cell)
        return self._execute_qry(qry)

    def execute(self) -> Result[StateKind, None] | Result[None, Exception]:
        """
        Executes the query and gets the state of the cell.

        Returns:
            Result: Success with StateKind or Failure with Exception
        """
        qry_result = self._qry_state_prop()
        state = StateKind.UNKNOWN if Result.is_failure(qry_result) else qry_result.data
        if self._ctl is not None:
            self._ctl.ctl_state = state
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return qry_result

    @property
    def cell(self) -> CalcCell:
        return self._cell
