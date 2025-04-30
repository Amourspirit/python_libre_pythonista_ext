from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from ooodev.utils.color import Color
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_default import QryColorBgDefault
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_default import QryColorBgDefault

    Color = int


class QryCtlStyleBgDefault(QryBase, QryCellT[Color]):
    """Gets the control name"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        # Cell is not currently used.
        # It is included here just in case color is set based on cell properties in the future.
        QryBase.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL

    def _get_color(self) -> Color:
        qry = QryColorBgDefault()
        return self._execute_qry(qry)

    def execute(self) -> Color:
        """
        Executes the query to get control name

        Returns:
            str: The control name
        """
        c = self._get_color()
        if self._ctl is not None:
            self._ctl.ctl_bg_color = c
        return c

    @property
    def cell(self) -> CalcCell:
        return self._cell
