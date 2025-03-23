from __future__ import annotations
from typing import Any, cast, List, TYPE_CHECKING
from com.sun.star.sheet import CellFlags

from ooodev.calc import CalcCell
from ooodev.events.args.event_args import EventArgs
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.utils.data_type.range_values import RangeValues
from ooodev.utils.helper.dot_dict import DotDict

from ...code.py_source_mgr import PyInstance
from ...code.py_source_mgr import PySource
from ...sheet.range.rng_util import RangeUtil
from ...ex import CellFormulaExpandError
from ...cell.state.ctl_state import CtlState
from ...cell.state.state_kind import StateKind
from ...style.default_style import DefaultStyle

if TYPE_CHECKING:
    from ...cell.cell_mgr import CellMgr
    from com.sun.star.sheet import SheetCellCursor
    import pandas as pd
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger

else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class ArrayBase(EventsPartial):
    """Manages Formula and Array for DataFrame."""

    def __init__(self, cell: CalcCell) -> None:
        """
        Constructor

        Args:
            cell (CalcCell): Calc Cell
        """
        EventsPartial.__init__(self)
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctl_state = CtlState(cell)
        self._cell_mgr = self._get_cell_mgr()
        self._style = DefaultStyle()

    def _get_cell_mgr(self) -> CellMgr:
        # avoid circular import
        from ...cell.cell_mgr import CellMgr

        return CellMgr(self.cell.calc_doc)

    def get_data(self) -> PySource:
        """
        Gets the data as a DotDict for a PySource instance.

        Returns:
            DotDict: Data as a DotDict
        """
        with self.log.indent(True):
            py_inst = PyInstance(self.cell.calc_doc)  # singleton
            py_src = py_inst[self.cell.cell_obj]
            return py_src  # .dd_data

    def get_rows_cols(self) -> List[int]:
        """
        Gets the number of rows and columns for a DataFrame.

        Returns:
            List[int]: Number of rows and columns
        """
        raise NotImplementedError

    def get_formula(self) -> str:
        """Gets the formula for the cell. any ``{`` and ``}`` are removed."""
        formula = self.cell.component.getFormula()
        if not formula:
            return ""
        formula = formula.lstrip("{").rstrip("}")
        return formula

    def set_formula_array(self, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Set the formula for the cell as an array formula.

        Other Args:
            **kwargs: Additional arguments that are passed to the event data.

        Raises:
            CellFormulaExpandError: If the range can not expand into the needed range.

        Note:
            Setting the formula array for the cell here will not update the cell control if there is one.
        """
        with self.log.indent(True):
            cm = self._cell_mgr
            # cm = CellMgr(self.cell.calc_doc)  # singleton
            formula = kwargs.pop("current_formula", None)
            add_style = bool(kwargs.pop("add_default_style", False))
            if not formula:
                formula = self.get_formula()
            if not formula:
                self.log.error("Cell %s has no formula.", self.cell.cell_obj)
                return
            self.log.debug("set_formula_array() Formula: %s", formula)
            cell_obj = self.cell.cell_obj
            rows, cols = self.get_rows_cols()
            ca = cell_obj.get_cell_address()
            rv = RangeValues(
                col_start=ca.Column,
                col_end=ca.Column + max(0, cols - 1),
                row_start=ca.Row,
                row_end=ca.Row + max(0, rows - 1),
            )
            ro = RangeObj.from_range(rv)

            cell_rng = self.cell.calc_sheet.get_range(range_obj=ro)

            rng_util = RangeUtil(doc=self.cell.calc_doc)
            if not rng_util.get_cell_can_expand(cell_rng):
                msg = f"Range can not expand into range: {ro}"
                if self.cell.calc_sheet.is_sheet_protected():
                    msg += " Sheet is protected. Cells may be protected or contain other data."
                else:
                    msg += " Cells may contain other data."
                self.log.error(msg)
                raise CellFormulaExpandError(msg)

            dd = DotDict()
            for key, value in kwargs.items():
                dd[key] = value
            dd.cell = self.cell
            with cm.listener_context(self.cell.component):
                self.cell.component.setFormula("")
                eargs = EventArgs(self)
                eargs.event_data = dd
                self.trigger_event("dispatch_removed_cell_formula", eargs)

                cell_rng.component.setArrayFormula(formula)
                eargs.event_data.range_obj = ro
                if add_style:
                    self._style.add_style_range(cell_rng)
                self.trigger_event("dispatch_add_array_formula", eargs)

    def set_formula(self, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Sets the formula for the cell.

        Other Args:
            **kwargs: Additional arguments that are passed to the event data.

        Note:
            Setting the formula for the cell here will not update the cell control if there is one.
        """
        with self.log.indent(True):
            formula = self.get_formula()
            if not formula:
                self.log.error("Cell %s has no formula.", self.cell.cell_obj)
                return
            cm = self._cell_mgr
            # cm = CellMgr(self.cell.calc_doc)  # singleton
            self.log.debug("set_formula() Formula: %s", formula)
            cursor = cast("SheetCellCursor", self.cell.calc_sheet.component.createCursorByRange(self.cell.component))  # type: ignore
            cursor.collapseToCurrentArray()
            dd = DotDict()
            for key, value in kwargs.items():
                dd[key] = value
            dd.cell = self.cell
            with cm.listener_context(self.cell.component):
                eargs = EventArgs(self)
                rng_addr = cursor.getRangeAddress()

                dd.range_obj = RangeObj.from_range(rng_addr)
                eargs.event_data = dd
                self.trigger_event("dispatch_remove_array_formula", eargs)
                del eargs.event_data["range_obj"]
                # cursor.setArrayFormula("")
                cursor.clearContents(CellFlags.DATETIME | CellFlags.VALUE | CellFlags.STRING | CellFlags.FORMULA)
                self.cell.component.setFormula(formula)
                self.trigger_event("dispatch_added_cell_formula", eargs)

    def get_formula_range(self) -> RangeObj:
        """
        Gets the range of the formula.
        This is the range of the formula in the cell and may not match the actual data range
        if the data has changed.

        Returns:
            RangeObj: The range of the formula.
        """
        cursor = cast("SheetCellCursor", self.cell.calc_sheet.component.createCursorByRange(self.cell.component))  # type: ignore
        cursor.collapseToCurrentArray()
        ca = cursor.getRangeAddress()
        ro = RangeObj.from_range(ca)
        return ro

    def update_required(self) -> bool:
        """
        Checks if the cell needs an update.

        If the cell is not an array formula, then an update is not needed.
        If the cell is not expanded as a array formula, then an update is not needed.
        If the cell is an array formula, then an update is needed if the data range has changed.

        Returns:
            bool: True if the cell needs an update.
        """
        if self._ctl_state.get_state() != StateKind.ARRAY:
            return False
        # this is an array formula
        # if the data column or row is not the same as the sheet range for the array
        # then an update is needed.
        rng = self.get_formula_range()
        rows_cols = self.get_rows_cols()
        return bool(rng.row_count != rows_cols[0] or rng.col_count != rows_cols[1])

    def update(self) -> None:
        """
        Updates the cell if needed.

        Calls ``update_required()`` to check if an update is needed.
        """
        with self.log.indent(True):
            if not self.update_required():
                # Warning: If this block is removed then sheets with multiple table will cycle updating endlessly.
                self.log.debug("No update needed.")
                return
            self.log.debug("Update needed.")
            formula = self.get_formula()
            cursor = cast("SheetCellCursor", self.cell.calc_sheet.component.createCursorByRange(self.cell.component))  # type: ignore
            cursor.collapseToCurrentArray()
            cm = self._cell_mgr
            # cm = CellMgr(self.cell.calc_doc)  # singleton
            with cm.listener_context(self.cell.component):
                self.log.debug("Clearing Array Formula")
                cursor.clearContents(
                    CellFlags.DATETIME | CellFlags.VALUE | CellFlags.STRING | CellFlags.FORMULA | CellFlags.STYLES
                )
                # clear the borders
                ro = RangeObj.from_range(cursor.getRangeAddress())
                cell_rng = self.cell.calc_sheet.get_range(range_obj=ro)
                self._style.remove_style_range(cell_rng)

            self.log.debug("Setting Formula Array")
            self.set_formula_array(current_formula=formula, add_default_style=True)

    # region Properties
    @property
    def ctl_state(self) -> CtlState:
        """Gets the control state."""
        return self._ctl_state

    @property
    def cell(self) -> CalcCell:
        """Gets the cell."""
        return self._cell

    @property
    def log(self) -> OxtLogger:
        """Gets the logger."""
        return self._log

    # endregion Properties
