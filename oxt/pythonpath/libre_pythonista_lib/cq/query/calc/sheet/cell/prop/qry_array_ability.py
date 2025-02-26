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


class QryArrayAbility(QryBase, QryCellT[bool]):
    """Gets the state of the cell"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query and gets the array ability of the cell.

        Returns:
            bool: The array ability of the cell.
                If an error occurs, False is returned.
                If the cell does not have a state, False is returned.
        """
        qry_km = QryKeyMaker()
        km = self._execute_qry(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.cell_array_ability_key, default=False)
        state = self._execute_qry(qry_state)
        result = False
        with contextlib.suppress(Exception):
            result = bool(state)
        return result

    @property
    def cell(self) -> CalcCell:
        return self._cell
