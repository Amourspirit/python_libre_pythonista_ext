from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.utils.data_type.range_values import RangeValues

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols import QryRowCols
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from oxt.pythonpath.libre_pythonista_lib.ex.exceptions import CellFormulaExpandError
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.sheet.range.rng_util import RangeUtil
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import (
        QryCellIsArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols import QryRowCols
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_array_formula import QryCellIsArrayFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_cell_is_formula import QryCellIsFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.ex.exceptions import CellFormulaExpandError
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.sheet.range.rng_util import RangeUtil
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


class CmdSetArrayFormula(CmdBase, LogMixin, CmdCellT):
    """
    Command to update a cell's array formula.

    Inherits from CmdBase for command functionality, LogMixin for logging, and CmdCellT for cell-specific operations.

    If the cell is a formula and not an array formula then it will be converted into an array formula.
    """

    def __init__(
        self, cell: CalcCell, rows: int = -1, cols: int = -1, formula: str | None = None, mod: PyModuleT | None = None
    ) -> None:
        """
        Initialize the command with a target cell.

        Args:
            cell: The CalcCell instance to operate on
            rows: One based number of rows in the array formula.
            cols: One based number of columns in the array formula.
            formula: The formula to set. If None, gets current formula. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._rows = rows
        self._cols = cols
        self._current_range_obj: RangeObj | None = None
        self._current_formula: str | None = None
        self._is_array_formula = cast(bool, None)
        self._is_formula = cast(bool, None)
        self._undo_available = False
        if formula:
            self._formula = formula.lstrip("{").rstrip("}")
        else:
            self._formula = None
        self.log.debug("init done for cell %s", self.cell.cell_obj)

    def _qry_formula_range(self) -> RangeObj:
        """Get the range object of the cell's array formula."""
        qry = QryFormulaRange(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            self.log.debug("_qry_formula_range() range obj: %s", qry_result.data)
            return qry_result.data
        raise qry_result.error

    def _qry_is_array_formula(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryCellIsArrayFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_is_formula(self) -> bool:
        """Check if the cell contains a formula."""
        qry = QryCellIsFormula(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_rows_cols(self) -> tuple[int, ...]:
        """Get the range object of the cell."""
        qry = QryRowCols(cell=self.cell, mod=self._mod)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return tuple(qry_result.data)
        raise qry_result.error

    def _get_range_values(self) -> RangeValues:
        """Get the range object of the cell."""
        ca = self._cell.cell_obj.get_cell_address()
        rv = RangeValues(
            col_start=ca.Column,
            col_end=ca.Column + max(0, self._cols - 1),
            row_start=ca.Row,
            row_end=ca.Row + max(0, self._rows - 1),
        )
        self.log.debug("_get_range_values() range values: %s", rv)
        return rv

    def _get_range_obj(self) -> RangeObj:
        """Get the range object of the cell."""
        rv = self._get_range_values()
        self.log.debug("_get_range_obj() range values: %s", rv)
        return RangeObj.from_range(rv)

    def _get_formula(self) -> str:
        """
        Get the cell's formula string without array formula braces.

        Raises:
            Exception: If cell has no formula.

        Returns:
            The formula string without surrounding braces
        """
        formula = ""
        if self._is_formula:
            formula = self.cell.component.getFormula()
        elif self._is_array_formula:
            ro = self._get_range_obj()
            cell_rng = self.cell.calc_sheet.get_range(range_obj=ro)
            formula = cell_rng.component.getArrayFormula()
        if not formula:
            raise Exception("Cell %s has no formula.", self.cell.cell_obj)
        return formula.lstrip("{").rstrip("}")

    def _set_array_formula(self) -> None:
        """
        Update an array formula.

        Returns:
            True if conversion successful, False otherwise
        """
        self.log.debug("Updating array formula")
        formula = cast(str, self._formula)

        ro = self._get_range_obj()
        cell_rng = self.cell.calc_sheet.get_range(range_obj=ro)
        rng_util = RangeUtil(doc=self.cell.calc_doc)
        if not rng_util.get_cell_can_expand(cell_rng):
            msg = f"Range can not expand into range: {ro}"
            if self.cell.calc_sheet.is_sheet_protected():
                msg += " Sheet is protected. Cells may be protected or contain other data."
            else:
                msg += " Cells may contain other data."
            raise CellFormulaExpandError(msg)

        code_listeners = CodeCellListeners(self.cell.calc_doc)
        with code_listeners.suspend_listener_ctx(self.cell):
            self.cell.component.setFormula("")
            cell_rng.component.setArrayFormula(formula)

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
            if self._rows <= 0 or self._cols <= 0:
                rows_cols = self._qry_rows_cols()
                self._rows = rows_cols[0]
                self._cols = rows_cols[1]

            if self._is_array_formula is None:
                self._is_array_formula = self._qry_is_array_formula()
                try:
                    self._current_range_obj = self._qry_formula_range()
                except Exception:
                    self._current_range_obj = None
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

            self._set_array_formula()

        except CellFormulaExpandError as e:
            self.log.warning(str(e))
            return
        except Exception:
            self.log.exception("Error setting formula for cell: %s", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo_set_formula(self) -> None:
        """
        Internal method to undo the formula update operation.
        Reverts the formula to its previous state.
        """
        if self._current_formula is None:
            self.log.debug("No Current State. Unable to undo.")
            return
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import (
                CmdSetFormula,
            )
        else:
            from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_formula import CmdSetFormula

        try:
            cmd = CmdSetFormula(cell=self.cell, formula=self._current_formula)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute undo command for cell %s.", self.cell.cell_obj)
                return
            self.log.debug("Successfully executed undo command for cell %s.", self.cell.cell_obj)
        except Exception:
            self.log.exception("Error undoing command for cell %s", self.cell.cell_obj)

    def _undo_set_array_formula(self) -> None:
        """
        Internal method to undo the formula update operation.
        Reverts the formula to its previous state.
        """
        if self._current_range_obj is None:
            self.log.debug("No Current State. Unable to undo.")
            return
        if self._current_formula is None:
            self.log.debug("No Current State. Unable to undo.")
            return
        cols = self._current_range_obj.col_count
        rows = self._current_range_obj.row_count

        cmd = CmdSetArrayFormula(cell=self.cell, rows=rows, cols=cols, formula=self._current_formula)
        self._execute_cmd(cmd)
        if not cmd.success:
            self.log.error("Failed to execute undo command for cell %s.", self.cell.cell_obj)
            return
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
            self.log.debug("No Current State. Unable to undo.")
            return

        self._current_range_obj = None
        self._current_formula = None
        self._undo_available = False

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell this command operates on.

        Returns:
            The CalcCell instance this command operates on
        """
        return self._cell
