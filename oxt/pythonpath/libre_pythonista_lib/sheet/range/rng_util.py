from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple

from ooodev.calc import CellObj, RangeObj, RangeValues
from ooodev.calc import CalcDoc, CalcCellRange
from ooodev.utils.data_type.rng.range_converter import RangeConverter

if TYPE_CHECKING:
    from com.sun.star.table import CellRangeAddress
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class RangeUtil:
    """
    Utility class for working Calc Ranges
    """

    def __init__(self, doc: CalcDoc) -> None:
        self._doc = doc
        self._convertor = None
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Init")

    def get_range(self, *args: CellObj) -> RangeObj:
        with self._log.indent(True):
            converter = self.converter
            return converter.get_range_obj(*args)

    def get_locked_cells(self, rng: CalcCellRange, *excludes: CellObj) -> Tuple[Tuple[int, int]]:
        """
        Get the locked cells in a range.

        Args:
            rng (CalcCellRange): The range.
            excludes (CellObj): The cells to exclude.

        Returns:
            Tuple[Tuple[int, int]]: The locked cells. Each element contains the row and column zero-based index of the locked cell.
        """
        with self._log.indent(True):
            # Access the specified sheet by name
            sheet = rng.calc_sheet.component

            # Get the range addresses
            rv = rng.range_obj.get_range_values()
            start_column = rv.col_start
            end_column = rv.col_end
            start_row = rv.row_start
            end_row = rv.row_end
            exclude_lst = []
            for exclude in excludes:
                ex_cv = exclude.get_cell_values()
                exclude_lst.append((ex_cv.row, ex_cv.col))
            omit = tuple(exclude_lst)
            locked = []
            # Iterate over each cell in the range
            for row in range(start_row, end_row + 1):
                for col in range(start_column, end_column + 1):
                    cell = sheet.getCellByPosition(col, row)
                    cv = (row, col)
                    if cv in omit:
                        continue
                    # Check if the cell is empty
                    if cell.CellProtection.IsLocked:  # type: ignore
                        locked.append(cv)
            return tuple(locked)

    def get_is_range_empty(self, rng: CalcCellRange) -> bool:
        """
        Returns the range from a cell address.

        Args:
            cell (str): The cell address.

        Returns:
            str: The range.
        """
        with self._log.indent(True):
            cursor = rng.create_cursor()
            ranges = cursor.component.queryEmptyCells()
            if ranges.getCount() != 1:
                if self._log.is_debug:
                    self._log.debug(f"get_is_range_empty(): ranges.getCount() != 1 {rng.range_obj}")
                return False
            try:
                cro = ranges.getByIndex(0)
                ca = cast("CellRangeAddress", cro.getRangeAddress())
                if self._log.is_debug:
                    self._log.debug(f"get_is_range_empty(): {rng.range_obj}")
                    self._log.debug(
                        f"get_is_range_empty() - Sheet: {ca.Sheet}, StartColumn: {ca.StartColumn}, StartRow: {ca.StartRow}, EndColumn: {ca.EndColumn}, EndRow: {ca.EndRow}"
                    )
                range_obj = RangeObj.from_range(ca)
                return range_obj == rng.range_obj
            except Exception:
                self._log.error(f"get_is_range_empty(): {rng.range_obj}", exc_info=True)
                return False

    def get_other_than_first_empty(self, rng: CalcCellRange) -> bool:
        """
        Get if all the cells except for the first one are empty.
        The first cell in the range is not checked.

        Args:
            cell (str): The cell address.

        Returns:
            bool: True if all the cells except for the first one are empty.
        """
        # check an see if we can expand right
        with self._log.indent(True):
            try:
                if rng.is_single_cell_range():
                    return True
                can_expand_right = False
                rng_vals = rng.range_obj.get_range_values()
                if rng.range_obj.start.right in rng.range_obj:
                    row_rng_vals = RangeValues(
                        col_start=rng_vals.col_start + 1,
                        col_end=rng_vals.col_end,
                        row_start=rng_vals.row_start,
                        row_end=rng_vals.row_start,
                    )
                    row_range_obj = RangeObj.from_range(row_rng_vals)
                    row_calc_range = rng.calc_sheet.get_range(range_obj=row_range_obj)
                    can_expand_right = self.get_is_range_empty(row_calc_range)
                    if self._log.is_debug:
                        self._log.debug(
                            f"get_other_than_first_empty(): can expand right is {can_expand_right} for {rng.range_obj}"
                        )
                    if can_expand_right is False:
                        return False
                elif self._log.is_debug:
                    self._log.debug(f"get_other_than_first_empty(): cannot expand right {rng.range_obj}")

                can_expand_down = False
                if rng.range_obj.start.down in rng.range_obj:
                    lower_rng_vals = RangeValues(
                        col_start=rng_vals.col_start,
                        col_end=rng_vals.col_end,
                        row_start=rng_vals.row_start + 1,
                        row_end=rng_vals.row_end,
                    )
                    lower_range_obj = RangeObj.from_range(lower_rng_vals)
                    lower_calc_range = rng.calc_sheet.get_range(range_obj=lower_range_obj)
                    can_expand_down = self.get_is_range_empty(lower_calc_range)
                    if self._log.is_debug:
                        self._log.debug(
                            f"get_other_than_first_empty(): can expand down is {can_expand_down} for {rng.range_obj}"
                        )
                    if can_expand_down is False:
                        return False
                elif self._log.is_debug:
                    self._log.debug(f"get_other_than_first_empty(): cannot expand down {rng.range_obj}")
                return can_expand_down is True or can_expand_right is True

            except Exception:
                self._log.error(f"get_other_than_first_empty(): {rng.range_obj}", exc_info=True)
            return False

    def get_cell_can_expand(self, rng: CalcCellRange) -> bool:
        """
        Get if the cell can expand. If the sheet is protected, it will check if any of the cells are locked.
        If no cells a locked, it will check if all the cells except for the first one are empty.

        Args:
            rng (CalcCellRange): The cell range.

        Returns:
            bool: True if the cell can expand.
        """
        with self._log.indent(True):
            sheet = rng.calc_sheet
            if sheet.is_sheet_protected():
                if self._log.is_debug:
                    self._log.debug(f"get_cell_can_expand(): Sheet is protected {rng.range_obj.sheet_name}")
                locked_cells = self.get_locked_cells(rng)
                if len(locked_cells) > 0:
                    if self._log.is_debug:
                        self._log.debug(f"get_cell_can_expand(): Locked cells {locked_cells}")
                    return False
            else:
                if self._log.is_debug:
                    self._log.debug(f"get_cell_can_expand(): Sheet is not protected {rng.range_obj.sheet_name}")

            other_then_first_empty = self.get_other_than_first_empty(rng)
            if self._log.is_debug:
                self._log.debug(f"get_cell_can_expand(): other_then_first_empty is {other_then_first_empty}")
            return other_then_first_empty

    @property
    def converter(self) -> RangeConverter:
        if self._convertor is None:
            self._convertor = RangeConverter()
        return self._convertor
