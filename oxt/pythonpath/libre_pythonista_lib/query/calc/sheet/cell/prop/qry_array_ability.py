from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class QryArrayAbility(QryT[bool]):
    """Gets the state of the cell"""

    def __init__(self, cell: CalcCell) -> None:
        self._kind = CalcQryKind.SIMPLE
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query and gets the array ability of the cell.

        Returns:
            bool: The array ability of the cell.
                If an error occurs, False is returned.
                If the cell does not have a state, False is returned.
        """
        qry_handler = QryHandler()
        qry_km = QryKeyMaker()
        km = qry_handler.handle(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.cell_array_ability_key, default=False)
        state = qry_handler.handle(qry_state)
        result = False
        with contextlib.suppress(Exception):
            result = bool(state)
        return result

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
