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
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName as CmdPropCodeName
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdCodeName(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl, overwrite_existing: bool = False) -> None:
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
        self._overwrite_existing = overwrite_existing
        self._success_commands: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._valid = self._validate()
        self._code_name = None
        self._current_dict_code_name = self.cell.extra_data.get("code_name", "")
        self._current_ctl: Union[Dict[str, Any], None] = None
        if self._valid:
            self._current_code_name = cast(Union[str, None], self._ctl.ctl_code_name)
        else:
            self._current_code_name = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        """
        Validates that the control has required attributes.

        Returns:
            bool: True if validation passes, False otherwise
        """
        required_attributes = {"cell", "ctl_code_name"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()
        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.debug("Validation warning. %s attribute is missing.", attrib)
                return False
        return True

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
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            cmd_prop_code_name = CmdPropCodeName(cell=self.cell, overwrite_existing=self._overwrite_existing)
            self._execute_cmd(cmd_prop_code_name)
            code_name = cmd_prop_code_name.get_gen_code_name()

            if cmd_prop_code_name.success:
                self._success_commands.append(cmd_prop_code_name)
            else:
                self.log.error("Error setting cell code name")
                return

            self._ctl.ctl_code_name = code_name
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
