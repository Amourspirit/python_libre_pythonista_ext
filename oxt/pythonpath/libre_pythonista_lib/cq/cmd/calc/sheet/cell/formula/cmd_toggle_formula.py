from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.calc import CalcCell, CalcCellRange
from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.style.default_style import DefaultStyle
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.draw_page.cmd_shape_visibility import CmdShapeVisibility
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_add_border_style import (
        CmdRngAddBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_remove_border_style import (
        CmdRngRemoveBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_add_border_style import (
        CmdCellAddBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_remove_border_style import (
        CmdCellRemoveBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
        CmdSetArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )


else:
    from ___lo_pip___.debug.break_mgr import BreakMgr
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_state import CmdState
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.style.default_style import DefaultStyle
    from libre_pythonista_lib.style.style_t import StyleT
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.cmd.calc.sheet.draw_page.cmd_shape_visibility import CmdShapeVisibility
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape
    from libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_add_border_style import CmdRngAddBorderStyle
    from libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_remove_border_style import (
        CmdRngRemoveBorderStyle,
    )
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_add_border_style import CmdCellAddBorderStyle
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.style.cmd_cell_remove_border_style import (
        CmdCellRemoveBorderStyle,
    )
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange

    PyModuleT = Any

break_mgr = BreakMgr()

break_mgr.add_breakpoint("libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_toggle_formula.execute")


class CmdToggleFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to toggle a cell's formula between normal and array formula states.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None, style: StyleT | None = None) -> None:
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
        self._success_cmds: list[CmdT] = []
        self._formula_state = StateKind.UNKNOWN  # 0: unknown, 1: normal formula, 2: array formula
        if style is None:
            self._style = DefaultStyle()
        else:
            self._style = style
        self.log.debug("init done for cell %s", self.cell.cell_obj)

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

    def _qry_formula_range(self) -> RangeObj:
        """Get the range object of the cell's array formula."""
        qry = QryFormulaRange(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def _cmd_set_state(self, state_kind: StateKind) -> bool:
        """Set the formula state."""
        cmd = CmdState(cell=self.cell, state=state_kind)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    def _cmd_set_cell_border_style(self) -> bool:
        """Set the cell border style."""
        cmd = CmdCellAddBorderStyle(cell=self.cell, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    def _cmd_remove_cell_border_style(self) -> bool:
        """Remove the cell border style."""
        cmd = CmdCellRemoveBorderStyle(cell=self.cell, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    def _cmd_add_range_border(self, cell_rng: CalcCellRange) -> bool:
        """Add the range border style."""
        cmd = CmdRngAddBorderStyle(rng=cell_rng, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    def _cmd_remove_range_border(self, cell_rng: CalcCellRange) -> bool:
        """Remove the range border style."""
        cmd = CmdRngRemoveBorderStyle(rng=cell_rng, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
        return cmd.success

    def _cmd_remove_style(self, kind: StateKind) -> bool:
        """Toggle the style based on the formula state."""
        rng = self._qry_formula_range()
        cell_rng = CalcCellRange(owner=self.cell.calc_sheet, rng=rng, lo_inst=self.cell.lo_inst)
        if kind == StateKind.PY_OBJ:
            if not self._cmd_remove_range_border(cell_rng):
                return False
        elif kind == StateKind.ARRAY and not self._cmd_remove_cell_border_style():
            return False
        return True

    def _cmd_add_style(self, kind: StateKind) -> bool:
        """Toggle the style based on the formula state."""
        if kind == StateKind.PY_OBJ:
            # not setting any border for single cell.
            return True
        rng = self._qry_formula_range()
        cell_rng = CalcCellRange(owner=self.cell.calc_sheet, rng=rng, lo_inst=self.cell.lo_inst)
        # if kind == StateKind.PY_OBJ:
        #     if self._cmd_set_cell_border_style():
        #         return True
        #     else:
        #         return False
        return not (kind == StateKind.ARRAY and not self._cmd_add_range_border(cell_rng))

    def _cmd_set_visibility(self, visible: bool) -> bool:
        """Set the visibility of the cell's shape."""
        qry = QryShape(cell=self.cell)
        qry_result = self._execute_qry(qry)
        if Result.is_failure(qry_result):
            return False
        shape_name = qry_result.data
        cmd = CmdShapeVisibility(sheet=self.cell.calc_sheet, shape_name=shape_name, visible=visible)
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

        try:
            is_formula = self._qry_is_formula()
            is_array_formula = self._qry_is_array_formula()
            if not is_formula and not is_array_formula:
                self.log.warning("Cell %s is not a formula cell. Nothing to do.", self.cell.cell_obj)
                self.success = False
                raise Exception("Cell %s is not a formula cell. Nothing to do.", self.cell.cell_obj)
            if is_formula:
                self._formula_state = StateKind.PY_OBJ
            elif is_array_formula:
                self._formula_state = StateKind.ARRAY

            if is_formula and not self._cmd_set_visibility(False):
                raise Exception("Failed to set visibility for cell %s.", self.cell.cell_obj)
            if is_array_formula and not self._cmd_set_visibility(True):
                raise Exception("Failed to set visibility for cell %s.", self.cell.cell_obj)

            if is_formula and not self._cmd_remove_style(StateKind.ARRAY):
                raise Exception("Failed to remove style for cell %s.", self.cell.cell_obj)
            if is_array_formula and not self._cmd_remove_style(StateKind.PY_OBJ):
                raise Exception("Failed to remove style for cell %s.", self.cell.cell_obj)

            if self._cmd is None:
                self._cmd = self._get_cmd(self.cell)
            if self._formula_state == StateKind.PY_OBJ:
                self._cmd_set_state(StateKind.ARRAY)
            elif self._formula_state == StateKind.ARRAY:
                self._cmd_set_state(StateKind.PY_OBJ)

            self._execute_cmd(self._cmd)
            if not self._cmd.success:
                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                raise Exception("Failed to execute command for cell %s.", self.cell.cell_obj)
            self._success_cmds.append(self._cmd)
            if is_formula and not self._cmd_add_style(StateKind.ARRAY):
                raise Exception("Failed to add style for cell %s.", self.cell.cell_obj)
            if is_array_formula and not self._cmd_add_style(StateKind.PY_OBJ):
                raise Exception("Failed to add style for cell %s.", self.cell.cell_obj)
        except Exception as e:
            self.log.warning("Error toggling formula for cell %s. %s", self.cell.cell_obj, e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the formula toggle operation.
        Reverts the formula to its previous state.
        """
        try:
            for cmd in reversed(self._success_cmds):
                self._execute_cmd_undo(cmd)
            self._success_cmds.clear()
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
