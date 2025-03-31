from __future__ import annotations
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_code_cell_listeners import QryCodeCellListeners
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )

else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_code_cell_listeners import QryCodeCellListeners
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_code_listener.py


class CmdCodeListenerDel(CmdBase, LogMixin, CmdCellT):
    """
    Command to delete Python code from a cell.

    Command will fail is the cell does not exist in the source manager.

    Args:
        cell (CalcCell): The target cell to append code to
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the command with a cell, module, and optional code and source provider.

        Args:
            cell (CalcCell): The target cell to append code to
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._state_changed = False
        self._current_has_listener = cast(bool, None)
        self.log.debug("init done for cell %s", self.cell.cell_obj)

    def _qry_code_listeners(self) -> CodeCellListeners:
        """
        Gets the code cell listeners via query.

        Returns:
            QryCodeCellListeners: The code cell listeners
        """
        qry = QryCodeCellListeners(self._cell.calc_doc)
        return self._execute_qry(qry)

    def _qry_code_name(self) -> Result[str, None] | Result[None, Exception]:
        """
        Query the code name for a cell.

        Args:
            calc_cell (CalcCell): Cell to query

        Returns:
            str: The cell's code name
        """
        qry = QryCodeName(cell=self._cell)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command to append code to the cell.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False
        code_name_result = self._qry_code_name()
        if Result.is_failure(code_name_result):
            self.log.error("Failed to get code name for cell %s", self.cell.cell_obj)
            return
        code_name = code_name_result.data

        listeners = self._qry_code_listeners()
        if self._current_has_listener is None:
            self._current_has_listener = code_name in listeners

        try:
            if self._current_has_listener:
                result = listeners.remove_listener(self.cell)
                if not result:
                    self.log.error("Failed to remove listener for cell %s", self.cell.cell_obj)
                    return

                self.log.debug("Successfully removed listener for cell %s", self.cell.cell_obj)
                self._state_changed = True
            else:
                self.log.debug("Listener not found for cell %s", self.cell.cell_obj)
        except Exception:
            self.log.exception("Error removing listener for cell %s", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """Internal method to undo the last code append operation"""
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            if self._current_has_listener is None:
                self.log.debug("Cell current listener check never occurred. Nothing to undo.")
                return
            if not self._current_has_listener:
                self.log.debug("Cell did not have a listener to restore. Nothing to undo.")
                return

            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import (
                    CmdCodeListener,
                )
            else:
                from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener import CmdCodeListener
            cmd = CmdCodeListener(cell=self.cell)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute undo command.")
                return
            self._current_has_listener = cast(bool, None)
            self._state_changed = False
            self.log.debug("Successfully executed undo command.")
        except Exception as e:
            self.log.exception("Error undoing command: %s", e)

    @override
    def undo(self) -> None:
        """
        Public undo method that only executes if the command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """Gets the cell this command operates on"""
        return self._cell
