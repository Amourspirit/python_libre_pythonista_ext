from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_pyc_rule import CmdPycRule
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin


class CmdRuleName(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the rule name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl, kind: RuleNameKind) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._rule_kind = kind

        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._current = self._ctl.ctl_rule_kind
        self._current_ctl: Union[Dict[str, Any], None] = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()

            if self._current == self._rule_kind:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.ctl_rule_kind = self._rule_kind

            cmd_orig_ctl = CmdPycRule(cell=self.cell, name=str(self._ctl.ctl_rule_kind))
            self._execute_cmd(cmd_orig_ctl)
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
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()
        try:
            if self._current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self._current_ctl)
                self._current_ctl = None

        except Exception:
            self.log.exception("Error executing undo command")
            return
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell
