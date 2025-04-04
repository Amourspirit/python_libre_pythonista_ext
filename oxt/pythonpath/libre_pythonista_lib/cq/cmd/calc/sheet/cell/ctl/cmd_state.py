from __future__ import annotations
from typing import Any, Dict, cast, List, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import (
        CmdCodeName as CmdPropCodeName,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState as CmdPropState
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName as CmdPropCodeName
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState as CmdPropState
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind


class CmdState(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl, state: StateKind) -> None:
        """
        Initialize the command to set a control's code name.

        Args:
            cell (CalcCell): The cell containing the control
            ctl (Ctl): The control to set the code name for
            overwrite_existing (bool, optional): If True, allows overwriting existing code names. Defaults to False.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._state = state
        self._success_commands: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._code_name = None
        self._current_ctl: Dict[str, Any] | None = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        """
        Validates that the control has required attributes.

        Returns:
            bool: True if validation passes, False otherwise
        """
        valid = self._state != StateKind.UNKNOWN
        if not valid:
            self.log.error("Validation error. state must not be StateKind.UNKNOWN.")
        return valid

    @override
    def execute(self) -> None:
        """
        Executes the command to set the control's code name.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False
        self._success_commands.clear()
        try:
            if not self._validate():
                return
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            cmd_prop_state = CmdPropState(cell=self.cell, state=self._state)
            self._execute_cmd(cmd_prop_state)
            if cmd_prop_state.success:
                self._success_commands.append(cmd_prop_state)
            else:
                self.log.error("Error setting cell code name")
                return

            self._ctl.ctl_state = self._state
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting code name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the command's changes.
        Restores the control's previous code name state.
        """
        for cmd in self._success_commands:
            self._execute_cmd_undo(cmd)
        self._success_commands.clear()
        if not self._state_changed:
            return
        try:
            if self._current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self._current_ctl)
                self._current_ctl = None
        except Exception:
            self.log.exception("Error undoing code name")
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        """
        Public method to undo the command if it was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell associated with the control.

        Returns:
            CalcCell: The cell containing the control
        """
        return self._ctl.cell
