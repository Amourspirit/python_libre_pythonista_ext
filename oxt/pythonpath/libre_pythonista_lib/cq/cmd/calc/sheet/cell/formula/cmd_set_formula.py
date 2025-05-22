from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Union

from com.sun.star.sheet import CellFlags

from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCellCursor  # service
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import (
        QryFormulaCursor,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import QryFormulaCursor
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result

    SheetCellCursor = Any


class CmdSetFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to update a cell's array formula.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.

    If the cell is a formula and not an array formula then it will be converted into an array formula.
    """

    def __init__(self, cell: CalcCell, formula: Union[str, None] = None) -> None:
        """
        Initialize the command with a target cell.

        Args:
            cell: The CalcCell instance to operate on
            formula: The formula to set. If None, gets current formula. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._undo_available = False
        self._current_formula: Union[str, None] = None
        self._is_array_formula = cast(bool, None)
        self._is_formula = cast(bool, None)
        self._current_col_rows = (0, 0)
        if formula:
            self._formula = formula.lstrip("{").rstrip("}")
        else:
            self._formula = None
        self.log.debug("init done for cell %s", self.cell.cell_obj)

    def _qry_is_array_formula(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_is_formula(self) -> bool:
        """Check if the cell contains a formula."""
        qry = QryCellIsFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_formula_cursor(self) -> SheetCellCursor:
        """Get the cursor for the cell's array formula range."""
        qry = QryFormulaCursor(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def _qry_formula_range(self) -> RangeObj:
        """Get the range object of the cell's array formula."""
        qry = QryFormulaRange(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

    def _get_cols_rows(self) -> tuple[int, int]:
        """Get the range object of the cell."""
        ro = self._qry_formula_range()
        return ro.col_count, ro.row_count

    def _get_formula(self) -> str:
        """
        Get the cell's formula string without array formula braces.

        Raises:
            Exception: If cell has no formula.

        Returns:
            The formula string without surrounding braces
        """
        formula = self.cell.component.getFormula()
        # if self._is_formula:
        #     formula = self.cell.component.getFormula()
        # elif self._is_array_formula:
        # don't know way but cell_rng.component.getArrayFormula()
        # does not work as expected.
        # It returns formula in format of '=PY.C(SHEET(),CELL("ADDRESS"),C1)'
        # Expected '=COM.GITHUB.AMOURSPIRIT.EXTENSIONS.LIBREPYTHONISTA.PYIMPL.PYC(SHEET();CELL("ADDRESS");C1)'
        # ro = self._qry_formula_range()
        # cell_rng = self.cell.calc_sheet.get_range(range_obj=ro)
        # formula = cell_rng.component.getArrayFormula()
        if not formula:
            raise Exception("Cell %s has no formula.", self.cell.cell_obj)
        result = formula.lstrip("{").rstrip("}")
        self.log.debug("_get_formula() formula: %s", result)
        return result

    def _set_formula(self) -> bool:
        """
        Set Formula.

        Returns:
            True if conversion successful, False otherwise
        """
        try:
            self.log.debug("Setting formula")
            code_listeners = CodeCellListeners(self.cell.calc_doc)

            formula = cast(str, self._formula)
            cursor = self._qry_formula_cursor()
            with code_listeners.suspend_listener_ctx(self.cell):
                cursor.clearContents(CellFlags.DATETIME | CellFlags.VALUE | CellFlags.STRING | CellFlags.FORMULA)
                cursor.gotoStart()
                self.cell.component.setFormula(formula)

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
        self._undo_available = True

        try:
            if self._is_array_formula is None:
                self._is_array_formula = self._qry_is_array_formula()
                try:
                    self._current_col_rows = self._get_cols_rows()
                except Exception:
                    self._current_col_rows = (0, 0)
                    self._undo_available = False

            if self._is_formula is None:
                self._is_formula = self._qry_is_formula()

            if self._is_formula or self._is_array_formula:
                try:
                    self._current_formula = self._get_formula()
                except Exception:
                    self._current_formula = None
                    self._undo_available = False

            if not self._formula:
                self._formula = self._get_formula()
            if not self._set_formula():
                return
        except Exception:
            self.log.exception("Error setting formula for cell: %s", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo_set_array_formula(self) -> None:
        """
        Internal method to undo the formula update operation.
        Reverts the formula to its previous state.
        """
        if self._current_formula is None:
            self.log.debug("No Current State. Unable to undo.")
            return
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
                CmdSetArrayFormula,
            )
        else:
            from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula

        cols, rows = self._get_cols_rows()
        cmd = CmdSetArrayFormula(cell=self.cell, rows=rows, cols=cols, formula=self._current_formula)
        self._execute_cmd(cmd)
        if not cmd.success:
            self.log.error("Failed to execute undo command for cell %s.", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed undo command for cell %s.", self.cell.cell_obj)

    def _undo_set_formula(self) -> None:
        """
        Internal method to undo the formula update operation.
        Reverts the formula to its previous state.
        """
        if self._current_formula is None:
            self.log.debug("No Current State. Unable to undo.")
            return
        self.cell.component.setFormula(self._current_formula)
        self.log.debug("Successfully executed undo command for cell %s.", self.cell.cell_obj)

    def _undo_no_formula(self) -> None:
        """
        Internal method to undo the formula update operation.
        Reverts the formula to its previous state.
        """
        self.cell.component.setFormula("")
        self.log.debug("Successfully executed undo command for cell %s.", self.cell.cell_obj)

    @override
    def undo(self) -> None:
        """
        Public undo method that executes only if the command was successful.
        """
        if not self.success:
            self.log.debug("Command not successful. Undo not needed.")
            return
        if not self._undo_available:
            self.log.debug("Undo not available.")
            return

        if self._is_array_formula:
            self._undo_set_array_formula()
        elif self._is_formula:
            self._undo_set_formula()
        else:
            self._undo_no_formula()

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell this command operates on.

        Returns:
            The CalcCell instance this command operates on
        """
        return self._cell
