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
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override


class CmdUpdateArrayFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to update a cell's array formula.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.

    If the cell is a formula and not an array formula then it will be converted into an array formula.
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

    def _qry_is_array_formula(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_is_formula(self) -> bool:
        """Check if the cell contains a formula."""
        qry = QryCellIsFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _get_formula(self) -> str:
        """
        Get the cell's formula string without array formula braces.

        Returns:
            The formula string without surrounding braces
        """
        formula = self.cell.component.getFormula()
        return formula.lstrip("{").rstrip("}")

    def _update_array_formula(self) -> bool:
        """
        Update an array formula.

        Returns:
            True if conversion successful, False otherwise
        """
        try:
            self.log.debug("Updating array formula")
            formula = self._get_formula()

            cursor = cast(
                "SheetCellCursor",
                self.cell.calc_sheet.component.createCursorByRange(
                    self.cell.component  # type: ignore
                ),
            )  # type: ignore
            cursor.collapseToCurrentArray()
            cursor.setArrayFormula(formula)
            return True
        except Exception:
            self.log.exception("Error updating array formula for cell: %s", self.cell.cell_obj)
        return False

    @override
    def execute(self) -> None:
        """
        Execute the update array formula command.

        Determines the current formula state and update to array formula.
        Sets success flag based on operation result.
        """
        self.success = False
        is_array_formula = self._qry_is_array_formula()
        is_formula = self._qry_is_formula()
        if not is_array_formula and not is_formula:
            self.log.error("Cell %s is not a array formula cell. Nothing to do.", self.cell.cell_obj)
            self.success = False
            return

        try:
            if not self._update_array_formula():
                return
        except Exception:
            self.log.exception("Error setting cell address")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        """
        Public undo method that executes only if the command was successful.
        """
        self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell this command operates on.

        Returns:
            The CalcCell instance this command operates on
        """
        return self._cell
