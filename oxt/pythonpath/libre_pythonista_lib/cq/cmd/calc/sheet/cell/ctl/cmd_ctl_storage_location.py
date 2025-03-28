from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_img_storage_location import (
        QryCtlStorageLocation,
    )
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_img_storage_location import QryCtlStorageLocation
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


class CmdCtlStorageLocation(CmdBase, LogMixin, CmdCellCtlT):
    """
    Command to manage storage location for a control in a cell.
    Inherits from CmdBase, LogMixin, and CmdCellCtlT.
    """

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
        self._current_state = cast(Dict[str, Any], None)

    def _qry_storage_location(self) -> str:
        """
        Queries the control name for the cell.

        Returns:
            str: The storage location of the control

        Raises:
            Exception: If the query fails
        """
        qry = QryCtlStorageLocation(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    @override
    def execute(self) -> None:
        """
        Executes the command to set the storage location.
        Sets success to True if operation succeeds, False otherwise.
        """
        self.success = False
        self._state_changed = False
        if self._current_state is None:
            self._current_state = self._ctl.copy_dict()
        try:
            self._ctl.ctl_storage_location = self._qry_storage_location()
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting control name")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the command's changes.
        Restores the control's previous code name state.
        """
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._state_changed = False
        try:
            if self._current_state is not None:
                self._ctl.clear()
                self._ctl.update(self._current_state)
                self._current_state = cast(Dict[str, Any], None)
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
