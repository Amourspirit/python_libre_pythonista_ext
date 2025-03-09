from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.units import SizePosMM100
from ooodev.units import UnitMM100

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


class QryCtlCellSizePos(QryBase, QryCellT[SizePosMM100]):
    """Gets the cell size and position"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL

    def _get_pos_size(self) -> SizePosMM100:
        ps = self.cell.component.Position
        size = self.cell.component.Size
        return SizePosMM100(
            x=UnitMM100(ps.X), y=UnitMM100(ps.Y), width=UnitMM100(size.Width), height=UnitMM100(size.Height)
        )

    def execute(self) -> SizePosMM100:
        """
        Executes the query to get cell size and position

        Returns:
            SizePosMM100: The cell size and position
        """
        value = self._get_pos_size()
        if self._ctl is not None:
            self._ctl.cell_pos_size = value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
