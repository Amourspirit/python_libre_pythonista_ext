from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_orig_ctl import QryOrigCtl


class QryCtlOrigRuleName(QryBase, LogMixin, QryCellT[str]):
    """Gets the control rule name"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL

    def execute(self) -> str:
        """
        Executes the query to get control rule name

        Returns:
            str: The control rule name
        """
        qry_shape = QryOrigCtl(cell=self.cell)
        value = self._execute_qry(qry_shape)
        if self._ctl is not None:
            try:
                kind = RuleNameKind(value)
                self._ctl.ctl_orig_rule_kind = kind
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            except Exception:
                self.log.exception("Error getting rule name")
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
