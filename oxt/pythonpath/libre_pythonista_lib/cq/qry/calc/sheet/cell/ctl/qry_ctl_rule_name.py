from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryCtlRuleName(QryBase, LogMixin, QryCellT[Result[RuleNameKind, None] | Result[None, Exception]]):
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

    def execute(self) -> Result[RuleNameKind, None] | Result[None, Exception]:
        """
        Executes the query to get control rule name

        Returns:
            Result: Success with control rule name or Failure with Exception
        """
        qry_shape = QryPycRule(cell=self.cell)
        result = self._execute_qry(qry_shape)
        if Result.is_failure(result):
            return result
        if self._ctl is not None:
            try:
                kind = RuleNameKind(result.data)
                self._ctl.ctl_rule_kind = kind
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            except Exception:
                self.log.exception("Error getting rule name")
        return result

    @property
    def cell(self) -> CalcCell:
        return self._cell
