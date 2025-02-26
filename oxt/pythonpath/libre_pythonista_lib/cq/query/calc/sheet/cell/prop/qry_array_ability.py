from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class QryArrayAbility(QryBase, QryCellT[bool | None]):
    """Gets the state of the cell"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> bool | None:
        """
        Executes the query and gets the array ability of the cell.

        Returns:
            bool | None: The array ability of the cell.
                If an error occurs, None is returned.
                If the cell does not have a state, None is returned.
        """
        qry_km = QryKeyMaker()
        km = self._execute_qry(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.cell_array_ability_key, default=None)
        return self._execute_qry(qry_state)

    @property
    def cell(self) -> CalcCell:
        return self._cell
