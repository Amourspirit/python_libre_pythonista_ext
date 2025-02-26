from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import (
        QryArrayAbility as QryPropArrayAbility,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_array_ability import (
        QryArrayAbility as QryPropArrayAbility,
    )
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT


class QryArrayAbility(QryBase, QryCellT[bool | None]):
    """Gets the array ability."""

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

    def execute(self) -> bool | None:
        """
        Executes the query to get array ability.

        Returns:
            bool | None: The Array Ability
        """
        qry_ability = QryPropArrayAbility(cell=self.cell)
        value = self._execute_qry(qry_ability)
        if self._ctl is not None:
            self._ctl.array_ability = value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
