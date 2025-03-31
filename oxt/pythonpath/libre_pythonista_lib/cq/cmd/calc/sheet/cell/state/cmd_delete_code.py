from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_cell_code import QryCellCode
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result

    PySourceManager = Any

# tested in: tests/test_cmd/test_cmd_append_code.py


class CmdDeleteCode(CmdBase, LogMixin, CmdCellT):
    """
    Command to delete Python code from a cell.

    Command will fail is the cell does not exist in the source manager.

    Args:
        cell (CalcCell): The target cell to append code to
        mod (PyModuleT): The Python module to associate the code with
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None) -> None:
        """
        Initialize the command with a cell, module, and optional code and source provider.

        Args:
            cell (CalcCell): The target cell to append code to
            mod (PyModuleT, optional): The Python module to associate the code with. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._py_src_mgr = cast(PySourceManager, None)
        self._state_changed = False
        self._current_source = cast(str | None, NULL_OBJ)
        self._src_code_removed = False
        self.log.debug("init done for cell %s", self.cell.cell_obj)

    def _qry_cell_code(self) -> str | None:
        """Gets the source code for the cell via query"""
        qry = QryCellCode(cell=self.cell, mod=self._mod)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    def _qry_mod(self) -> PyModuleT:
        """
        Gets the Python module via query.

        Returns:
            PyModuleT: The default Python module for the document
        """
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Gets a PySourceManager instance for the current module.

        Returns:
            PySourceManager: A singleton instance keyed by module
        """
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
        qry = QryPySrcMgrCode(cell=self.cell, mod=self._mod)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command to append code to the cell.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False
        self._src_code_removed = False
        if self._mod is None:
            self._mod = self._qry_mod()

        try:
            if self._py_src_mgr is None:
                self._py_src_mgr = self._qry_py_src_mgr()
            if self._current_source is NULL_OBJ:
                self._current_source = self._qry_cell_code()
            self._py_src_mgr.remove_source_by_calc_cell(self.cell)
            self._src_code_removed = True
            if self.cell.cell_obj in self._py_src_mgr:
                del self._py_src_mgr[self.cell.cell_obj]
                self.log.debug("Successfully removed source code from source manager.")
            else:
                self.log.debug("Source code not found in source manager.")
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting cell address")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """Internal method to undo the last code append operation"""
        try:
            if not self._state_changed:
                self.log.debug("State is already set. Undo not needed.")
                return
            if not isinstance(self._current_source, str):
                self.log.warning("Current source is None. Nothing to undo.")
                return

            if not self._src_code_removed:
                self.log.warning("Source code was not removed. Nothing to undo.")
                return

            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import (
                    CmdAppendCode,
                )
            else:
                from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_append_code import CmdAppendCode

            cmd = CmdAppendCode(cell=self.cell, mod=self._mod, code=self._current_source)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute undo command.")
                return
            self._current_source = cast(str | None, NULL_OBJ)
            self._state_changed = False
            self._src_code_removed = False
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
