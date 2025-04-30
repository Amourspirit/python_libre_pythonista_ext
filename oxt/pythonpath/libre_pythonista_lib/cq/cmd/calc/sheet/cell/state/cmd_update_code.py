from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.utils.custom_ext import override

    PySourceManager = Any


# tested in: tests/test_cmd/test_cmd_append_code.py


class CmdUpdateCode(CmdBase, LogMixin, CmdCellT):
    """
    Command to update Python code for a cell.

    Command will fail is the cell does not exist in the source manager.

    Args:
        cell (CalcCell): The target cell to append code to
        mod (PyModuleT, optional): The Python module to associate the code with. Defaults to None.
        code (str, optional): The Python code to append. Defaults to empty string
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None, code: str = "") -> None:
        """
        Initialize the command with a cell, module, and optional code and source provider.

        Args:
            cell (CalcCell): The target cell to append code to
            mod (PyModuleT, optional): The Python module to associate the code with. Defaults to None.
            code (str, optional): The Python code to append. Defaults to empty string
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._code = code
        self._py_src_mgr = cast(PySourceManager, None)
        self._state_changed = False
        self._current_state = cast(str | None, None)
        self.log.debug("init done for cell %s", cell.cell_obj)

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
        qry = QryPySrcMgrCode(doc=self.cell.calc_doc, mod=self._mod)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command to update code for a cell.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False
        if self._mod is None:
            self._mod = self._qry_mod()

        try:
            if self._py_src_mgr is None:
                self._py_src_mgr = self._qry_py_src_mgr()
            if not self.cell.cell_obj in self._py_src_mgr:
                self.log.warning("Cell %s does not exist in source manager. Nothing to update.", self.cell.cell_obj)
                return
            if self._current_state is None:
                self._current_state = self._py_src_mgr[self.cell.cell_obj].source_code

            self._py_src_mgr.update_source(code=self._code, cell_obj=self.cell.cell_obj)
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

            if self._current_state is None:
                self.log.warning("Current state is None. Nothing to undo.")
                return

            if self._py_src_mgr is None:
                self._py_src_mgr = self._qry_py_src_mgr()

            self._py_src_mgr.update_source(code=self._current_state, cell_obj=self.cell.cell_obj)
            self._current_state = None
            self._state_changed = False
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell address")

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
