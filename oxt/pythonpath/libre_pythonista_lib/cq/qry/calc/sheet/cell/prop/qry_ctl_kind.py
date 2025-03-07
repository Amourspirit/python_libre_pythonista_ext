from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.ctl_kind import CtlKind


class QryCtlKind(QryBase, QryCellT[CtlKind]):
    """Gets the kind of the control for the cell"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> CtlKind:
        """
        Executes the query and gets the pyc rule of the cell.

        Returns:
            CtlKind: The kind of the control for the cell. If the control is not found, then ``CtlKind.UNKNOWN`` is returned.
        """
        qry = QryPycRule(self._cell)
        result = self._execute_qry(qry)
        return CtlKind.from_rule_name_kind(result)

    @property
    def cell(self) -> CalcCell:
        return self._cell
