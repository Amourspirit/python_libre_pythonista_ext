from __future__ import annotations
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from com.sun.star.sheet import SheetCellCursor  # service
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_array_formula import (
        CmdUpdateArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_is_pyc_array_formula import QryCellIsPycArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_update_array_formula import CmdUpdateArrayFormula
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdToggleFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to toggle a cell's formula between normal and array formula states.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.
    """

    def __init__(self, cell: CalcCell) -> None:
        """
        Initialize the command with a target cell.

        Args:
            cell: The CalcCell instance to operate on
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._formula_state = 0  # 0: unknown, 1: normal formula, 2: array formula

    def _qry_is_formula(self) -> bool:
        """Check if the cell contains a formula."""
        qry = QryCellIsFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_is_array_formula(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _get_formula(self) -> str:
        """
        Get the cell's formula string without array formula braces.

        Returns:
            The formula string without surrounding braces
        """
        formula = self.cell.component.getFormula()
        return formula.lstrip("{").rstrip("}")

    def _formula_to_array(self) -> bool:
        """
        Convert a normal formula to an array formula.

        Returns:
            True if conversion successful, False otherwise
        """
        cmd = CmdUpdateArrayFormula(cell=self.cell)
        self._execute_cmd(cmd)
        return cmd.success

    def _array_to_formula(self) -> bool:
        """
        Convert an array formula to a normal formula.

        Returns:
            True if conversion successful, False otherwise
        """
        try:
            self.log.debug("Converting to array formula")
            formula = self._get_formula()
            self.cell.component.setFormula(formula)
            return True
        except Exception as e:
            self.log.exception("Error converting array formula to formula: %s", e)
        return False

    @override
    def execute(self) -> None:
        """
        Execute the formula toggle command.

        Determines the current formula state and toggles between normal and array formula.
        Sets success flag based on operation result.
        """
        self.success = False
        self._formula_state = 0
        is_formula = self._qry_is_formula()
        is_array_formula = self._qry_is_array_formula()
        if not is_formula and not is_array_formula:
            self.log.error("Cell %s is not a formula cell. Nothing to do.", self.cell.cell_obj)
            self.success = False
            return
        if is_formula:
            self._formula_state = 1
        elif is_array_formula:
            self._formula_state = 2

        try:
            if self._formula_state == 1:
                if not self._formula_to_array():
                    return
            elif self._formula_state == 2 and not self._array_to_formula():
                return
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
            if self._formula_state == 0:
                self.log.debug("No formula state for cell %s. Nothing to undo.", self.cell.cell_obj)
                return
            if self._formula_state == 1:
                _ = self._array_to_formula()
            elif self._formula_state == 2:
                _ = self._formula_to_array()
            self._formula_state = 0
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
