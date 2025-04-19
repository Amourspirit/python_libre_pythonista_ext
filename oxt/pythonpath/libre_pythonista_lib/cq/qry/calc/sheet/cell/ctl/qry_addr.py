from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr as QryPropAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr as QryPropAddr
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from libre_pythonista_lib.utils.result import Result


class QryAddr(QryBase, QryCellT[Result[Addr, None] | Result[None, Exception]]):
    """Gets the Address of the cell such as ``sheet_index=0&cell_addr=A1``"""

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

    def execute(self) -> Result[Addr, None] | Result[None, Exception]:
        """
        Executes the query to get address

        Returns:
            Result: Success with address or Failure with Exception
        """
        qry_shape = QryPropAddr(cell=self.cell)
        result = self._execute_qry(qry_shape)
        if Result.is_failure(result):
            return result
        if self._ctl is not None:
            self._ctl.addr = result.data.value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return result

    @property
    def cell(self) -> CalcCell:
        return self._cell
