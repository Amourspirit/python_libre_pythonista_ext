from __future__ import annotations
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


# tested in: tests/test_cmd/test_cmd_append_code.py


class CmdUpdateCode(CmdBase, LogMixin, CmdCellT):
    """
    Command to update Python code for a cell.

    Command will fail is the cell does not exist in the source manager.

    Args:
        cell (CalcCell): The target cell to append code to
        mod (PyModuleT): The Python module to associate the code with
        code (str, optional): The Python code to append. Defaults to empty string
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT, code: str = "") -> None:
        """
        Initialize the command with a cell, module, and optional code and source provider.

        Args:
            cell (CalcCell): The target cell to append code to
            mod (PyModuleT): The Python module to associate the code with
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

    def _get_py_src_mgr(self) -> PySourceManager:
        """Gets a PySourceManager instance for the current module"""
        # singleton keyed by module
        return PySourceManager(doc=self.cell.calc_doc, mod=self._mod)

    @override
    def execute(self) -> None:
        """
        Executes the command to update code for a cell.
        Sets success flag to True if successful, False otherwise.
        """
        self.success = False
        self._state_changed = False

        try:
            if not isinstance(self._py_src_mgr, PySourceManager):
                self._py_src_mgr = self._get_py_src_mgr()
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

            if not isinstance(self._py_src_mgr, PySourceManager):
                self._py_src_mgr = self._get_py_src_mgr()

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
