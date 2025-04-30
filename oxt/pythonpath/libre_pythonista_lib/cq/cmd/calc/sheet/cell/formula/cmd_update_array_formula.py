from __future__ import annotations
from typing import TYPE_CHECKING, Any

from com.sun.star.sheet import CellFlags
from ooodev.calc import CalcCell, CalcCellRange
from ooodev.utils.data_type.range_obj import RangeObj

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCellCursor  # service
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_is_update_required import (
        QryIsUpdateRequired,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import (
        CmdSetArrayFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_remove_border_style import (
        CmdRngRemoveBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_add_border_style import (
        CmdRngAddBorderStyle,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_formula import QryCellFormula
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import (
        QryFormulaCursor,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import (
        QryFormulaRange,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.formula.qry_is_update_required import QryIsUpdateRequired
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.formula.cmd_set_array_formula import CmdSetArrayFormula
    from libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_remove_border_style import CmdRngRemoveBorderStyle
    from libre_pythonista_lib.cq.cmd.calc.sheet.range.style.cmd_rng_add_border_style import CmdRngAddBorderStyle
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_formula import QryCellFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_cursor import QryFormulaCursor
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_formula_range import QryFormulaRange
    from libre_pythonista_lib.utils.result import Result

    SheetCellCursor = Any


class CmdUpdateArrayFormula(CmdBase, LogMixin, CmdCellT):
    def __init__(self, cell: CalcCell, style: StyleT | None = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._cell = cell
        self._style = style
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_is_update_required(self) -> bool:
        """Check if the cell contains an array formula."""
        qry = QryIsUpdateRequired(cell=self.cell)
        return self._execute_qry(qry)

    def _qry_cell_formula(self) -> str:
        """Get the formula for the cell."""
        qry = QryCellFormula(cell=self.cell.component)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        raise qry_result.error

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

    def _cmd_remove_range_border(self, cell_rng: CalcCellRange) -> bool:
        """Remove the range border style."""
        cmd = CmdRngRemoveBorderStyle(rng=cell_rng, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self.log.debug("Successfully executed CmdRngRemoveBorderStyle command.")
        else:
            self.log.error("Failed to execute CmdRngRemoveBorderStyle command.")
        return cmd.success

    def _cmd_add_range_border(self, cell_rng: CalcCellRange) -> bool:
        """Add the range border style."""
        cmd = CmdRngAddBorderStyle(rng=cell_rng, style=self._style)
        self._execute_cmd(cmd)
        if cmd.success:
            self.log.debug("Successfully executed CmdRngAddBorderStyle command.")
        else:
            self.log.error("Failed to execute CmdRngAddBorderStyle command.")
        return cmd.success

    @override
    def execute(self) -> None:
        self.success = False
        try:
            if not self._qry_is_update_required():
                self.log.debug("No update required.")
                self.success = True
                return
            formula = self._qry_cell_formula()
            cursor = self._qry_formula_cursor()
            rng = self._qry_formula_range()
            code_listeners = CodeCellListeners(self.cell.calc_doc)

            with code_listeners.suspend_listener_ctx(self.cell):
                cursor.clearContents(
                    CellFlags.DATETIME | CellFlags.VALUE | CellFlags.STRING | CellFlags.FORMULA | CellFlags.STYLES
                )
                self.cell.component.setFormula(formula)

            cell_rng = CalcCellRange(owner=self.cell.calc_sheet, rng=rng, lo_inst=self.cell.lo_inst)

            self._cmd_remove_range_border(cell_rng)

            cmd = CmdSetArrayFormula(cell=self.cell, formula=formula)
            self._execute_cmd(cmd)
            if not cmd.success:
                self.log.error("Failed to execute command for cell %s.", self.cell.cell_obj)
                return

            rng = self._qry_formula_range()
            cell_rng = CalcCellRange(owner=self.cell.calc_sheet, rng=rng, lo_inst=self.cell.lo_inst)
            self._cmd_add_range_border(cell_rng)
        except Exception:
            self.log.exception("Error updating array formula for cell %s.", self.cell.cell_obj)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    @override
    def undo(self) -> None:
        self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
