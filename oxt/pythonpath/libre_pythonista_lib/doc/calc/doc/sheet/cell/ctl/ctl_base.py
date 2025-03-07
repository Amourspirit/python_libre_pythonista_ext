from __future__ import annotations
from typing import Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mixin.calc_cell_mixin import CalcCellMixin
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.ctl_kind import CtlKind


class CtlBase(LogMixin, CalcCellMixin):
    def __init__(self, ctl: Ctl) -> None:
        LogMixin.__init__(self)
        CalcCellMixin.__init__(self, ctl.cell)
        self._ctl = ctl
        self.__ctl_kind = None

    def supports_prop(self, prop: CtlPropKind) -> bool:
        """Checks if the control supports the given property."""
        return self._ctl.supports_prop(prop)

    # region Properties
    @property
    def ctl(self) -> Ctl:
        return self._ctl

    @property
    def array_ability(self) -> bool:
        return self.ctl.array_ability

    @property
    def control_kind(self) -> CtlKind:
        """Gets the control kind."""
        return self.ctl.control_kind

    @property
    def ctl_props(self) -> Tuple[CtlPropKind, ...]:
        """Gets the control properties."""
        return self.ctl.ctl_props

    @property
    def code_name(self) -> str:
        return self.ctl.ctl_code_name

    @property
    def addr(self) -> str:
        return self.ctl.addr

    @property
    def modify_trigger_event(self) -> RuleNameKind:
        return self.ctl.modify_trigger_event

    @property
    def rule_kind(self) -> RuleNameKind:
        return self.ctl.ctl_rule_kind

    @property
    def orig_rule_kind(self) -> RuleNameKind:
        return self.ctl.ctl_orig_rule_kind

    @property
    def ctl_kind(self) -> CtlKind:
        """Gets the control kind."""
        if self.__ctl_kind is None:
            self.__ctl_kind = CtlKind.from_rule_name_kind(self.rule_kind)
        return self.__ctl_kind

    # endregion Properties
