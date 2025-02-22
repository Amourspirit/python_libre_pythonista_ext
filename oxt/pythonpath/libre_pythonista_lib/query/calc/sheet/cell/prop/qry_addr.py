from __future__ import annotations
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


class QryAddr(QryT[str]):
    """Gets the address of the cell such as ``sheet_index=0&cell_addr=A1"``"""

    def __init__(self, cell: CalcCell) -> None:
        self._kind = CalcQryKind.SIMPLE
        self._cell = cell

    def execute(self) -> str:
        """
        Executes the query and gets the address of the cell.

        Returns:
            str: The address of the cell.
        """
        qry_handler = QryHandler()
        qry_km = QryKeyMaker()
        km = qry_handler.handle(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.cell_addr_key, default="")
        return str(qry_handler.handle(qry_state))

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
