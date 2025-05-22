from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT


class QryLblDefault(QryBase, QryCellT[str]):
    """Gets the default label of the cell such as ``<>``"""

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

    def execute(self) -> str:
        """
        Executes the query to get default label

        Returns:
            str: The default label
        """
        value = "<>"
        if self._ctl is not None:
            self._ctl.label = value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
