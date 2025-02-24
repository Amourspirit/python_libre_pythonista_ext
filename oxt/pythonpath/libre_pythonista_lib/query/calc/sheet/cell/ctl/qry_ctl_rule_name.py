from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
else:
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule


class QryCtlRuleName(LogMixin, QryCellT[str]):
    """Gets the control rule name"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self._kind = CalcQryKind.CELL
        self._qry_handler = QryHandler()

    def execute(self) -> str:
        """
        Executes the query to get control rule name

        Returns:
            str: The control rule name
        """
        qry_shape = QryPycRule(cell=self.cell)
        name = self._qry_handler.handle(qry_shape)
        if self._ctl is not None:
            try:
                kind = RuleNameKind(name)
                self._ctl.ctl_rule_kind = kind
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            except Exception:
                self.log.exception("Error getting rule name")
        return name

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.CELL``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
