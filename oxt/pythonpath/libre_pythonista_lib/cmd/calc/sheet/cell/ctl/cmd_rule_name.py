from __future__ import annotations
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin


class CmdRuleName(LogMixin, CmdCellCtlT):
    """Sets the rule name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl, kind: RuleNameKind) -> None:
        LogMixin.__init__(self)
        self._ctl = ctl
        self._success = False
        self._rule_kind = kind

        self._kind = CalcCmdKind.SIMPLE
        self._cmd_handler = CmdHandler()
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._current = self._ctl.ctl_rule_kind

    def execute(self) -> None:
        self._success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            if self._current == self._rule_kind:
                self.log.debug("State is already set.")
                self._success = True
                return
            self._ctl.ctl_rule_kind = self._rule_kind

            cmd_orig_ctl = CmdPycRule(cell=self.cell, name=str(self._ctl.ctl_rule_kind))
            self._cmd_handler.handle(cmd_orig_ctl)
            if cmd_orig_ctl.success:
                self._success_cmds.append(cmd_orig_ctl)
            else:
                raise Exception("Error setting cell shape name")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting control shape name: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            cmd.undo()
        self._success_cmds.clear()
        self._ctl.ctl_rule_kind = self._current
        self.log.debug("Successfully executed undo command.")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.SIMPLE``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
