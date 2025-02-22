from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.query.qry_t import QryT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cell.state.state_kind import StateKind
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class QryState(QryT[StateKind]):
    """Gets the state of the cell"""

    def __init__(self, cell: CalcCell) -> None:
        self._kind = CalcQryKind.SIMPLE
        self._cell = cell

    def execute(self) -> StateKind:
        """
        Executes the query and gets the state of the cell.

        Returns:
            StateKind: The state of the cell.
                If an error occurs, ``StateKind.UNKNOWN`` is returned.
                If the cell does not have a state, ``StateKind.UNKNOWN`` is returned.
        """
        qry_handler = QryHandler()
        qry_km = QryKeyMaker()
        km = qry_handler.handle(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.ctl_state_key, default=StateKind.UNKNOWN.value)
        state = qry_handler.handle(qry_state)
        result = None
        with contextlib.suppress(Exception):
            result = StateKind(state)
        if result is None:
            return StateKind.UNKNOWN
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
