from __future__ import annotations
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import (
        CmdArrayAbility as CmdPropArrayAbility,
    )
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_array_ability import (
        CmdArrayAbility as CmdPropArrayAbility,
    )


class CmdArrayAbility(CmdBase, LogMixin, CmdCellCtlT):
    """
    Sets the array ability.

    Assigns the array ability to the control as property ``array_ability``.
    """

    def __init__(self, cell: CalcCell, ctl: Ctl, ability: bool) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._ability = ability
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current = self._ctl.array_ability

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            if self._current == self._ability:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.array_ability = self._ability

            array_ability_cmd = CmdPropArrayAbility(cell=self.cell, ability=self._ctl.array_ability)
            self._execute_cmd(array_ability_cmd)
            if array_ability_cmd.success:
                self._success_cmds.append(array_ability_cmd)
            else:
                raise Exception("Error setting array ability")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting array ability: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            cmd.undo()
        self._success_cmds.clear()
        self._ctl.array_ability = self._current
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
