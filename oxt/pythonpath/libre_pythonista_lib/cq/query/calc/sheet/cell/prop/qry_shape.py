from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.query.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_key_maker import QryKeyMaker


class QryShape(QryBase, QryCellT[str]):
    """Gets the shape of the cell such as ``SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf``"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> str:
        """
        Executes the query and gets the shape of the cell.

        Returns:
            str: The shape of the cell.
        """
        qry_km = QryKeyMaker()
        km = self._execute_qry(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.ctl_shape_key, default="")
        return str(self._execute_qry(qry_state))

    @property
    def cell(self) -> CalcCell:
        return self._cell
