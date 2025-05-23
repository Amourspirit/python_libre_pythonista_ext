from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING, Union

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_control_img_name import QryControlImgName
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_control_img_name import QryControlImgName
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


class CmdControlImgName(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        """
        Initialize the command to set a control name.

        Args:
            cell (CalcCell): The cell containing the control
            ctl (Ctl): The control to set the code name for
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._code_name = None
        self._current_control_name = cast(Union[str, None], NULL_OBJ)
        self._current_ctl: Union[Dict[str, Any], None] = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_control_name(self) -> str:
        """Queries the control name for the cell"""
        qry = QryControlImgName(cell=self.cell, ctl=self._ctl)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    @override
    def execute(self) -> None:
        """
        Executes the command to set the control name.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False
        if self._current_control_name is NULL_OBJ:
            self._current_control_name = self._ctl.ctl_name
        ctl_name = None
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            ctl_name = self._qry_control_name()
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting control name")
            return
        self.log.debug("Successfully executed command for cell %s. Control name: %s", self.cell.cell_obj, ctl_name)
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the command's changes.
        Restores the control's previous code name state.
        """
        if not self._state_changed:
            return
        try:
            if self._current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self._current_ctl)
                self._current_ctl = None
        except Exception:
            self.log.exception("Error undoing control name")
            return
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
