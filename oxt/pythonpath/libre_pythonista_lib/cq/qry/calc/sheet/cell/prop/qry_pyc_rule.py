from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind


class QryPycRule(QryBase, QryCellT[RuleNameKind]):
    """Gets the pyc rule of the cell such as ``CELL_DATA_TYPE_STR``"""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> RuleNameKind:
        """
        Executes the query and gets the pyc rule of the cell.

        Returns:
            RuleNameKind: The pyc rule of the cell. If the rule is not found, then ``RuleNameKind.UNKNOWN`` is returned.
        """
        qry_km = QryKeyMaker()
        km = self._execute_qry(qry_km)
        qry_state = QryCellPropValue(cell=self._cell, name=km.pyc_rule_key, default="")
        result = str(self._execute_qry(qry_state))
        return RuleNameKind.from_str(result)

    @property
    def cell(self) -> CalcCell:
        return self._cell
