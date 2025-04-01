from __future__ import annotations
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
        CmdSetArrayFormula,
    )


else:
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override

    PyModuleT = Any

break_mgr = BreakMgr()

break_mgr.add_breakpoint("libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_toggle_formula.execute")


class CmdToggleFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to toggle a cell's formula between normal and array formula states.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None) -> None:
        """
        Initialize the command with a target cell.

        Args:
            cell: The CalcCell instance to operate on
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._cmd: CmdCellT | None = None
        self._success_cmds: list[CmdCellT] = []
        self._formula_state = StateKind.UNKNOWN  # 0: unknown, 1: normal formula, 2: array formula

    def _get_cmd(self, cell: CalcCell) -> CmdCellT:
        """Get the appropriate command based on the current formula state."""
        if self._formula_state == StateKind.PY_OBJ:
            self.log.debug("_get_cmd() Returning CmdSetArrayFormula")
            return CmdSetArrayFormula(cell=cell, mod=self._mod)
        elif self._formula_state == StateKind.ARRAY:
            self.log.debug("_get_cmd() Returning CmdSetFormula")
            return CmdSetFormula(cell=cell)
        else:
            raise ValueError("_get_cmd() Unknown formula state")

    def _qry_is_formula(self) -> bool:
        """Check if the cell contains a formula."""
        qry = QryCellIsFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_is_array_formula(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _cmd_set_state(self, state_kind: StateKind) -> bool:
        """Set the formula state."""
        cmd = CmdState(cell=self.cell, state=state_kind)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    @override
    def execute(self) -> None:
        """
        Execute the formula toggle command.

        Determines the current formula state and toggles between normal and array formula.
        Sets success flag based on operation result.
        """
        # break_mgr.check_breakpoint("libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_toggle_formula.execute")
        self.success = False
        self._success_cmds.clear()
        self._formula_state = StateKind.UNKNOWN
        is_formula = self._qry_is_formula()
        is_array_formula = self._qry_is_array_formula()
        if not is_formula and not is_array_formula:
            self.log.warning("Cell %s is not a formula cell. Nothing to do.", self.cell.cell_obj)
            self.success = False
            return
        if is_formula:
            self._formula_state = StateKind.PY_OBJ
        elif is_array_formula:
            self._formula_state = StateKind.ARRAY

        try:
            if self._cmd is None:
                self._cmd = self._get_cmd(self.cell)
            if self._formula_state == StateKind.PY_OBJ:
                self._cmd_set_state(StateKind.ARRAY)
            elif self._formula_state == StateKind.ARRAY:
                self._cmd_set_state(StateKind.PY_OBJ)

            self._execute_cmd(self._cmd)
            if not self._cmd.success:
                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                return
            self._success_cmds.append(self._cmd)
        except Exception:
            self.log.exception("Error setting cell address")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the formula toggle operation.
        Reverts the formula to its previous state.
        """
        try:
            if self._cmd is None:
                self.log.debug("No Current State. Unable to undo.")
                return
            self._execute_cmd_undo(self._cmd)
            self._cmd = None
            self.success = False
            self._formula_state = StateKind.UNKNOWN
            self.log.debug("Successfully executed undo command for cell %s.", self.cell.cell_obj)
        except Exception:
            self.log.exception("Error undoing command for cell %s", self.cell.cell_obj)

    @override
    def undo(self) -> None:
        """
        Public undo method that executes only if the command was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell this command operates on.

        Returns:
            The CalcCell instance this command operates on
        """
        return self._cell
