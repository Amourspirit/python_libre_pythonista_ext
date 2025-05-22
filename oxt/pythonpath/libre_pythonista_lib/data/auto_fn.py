from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcCellRange
from ooodev.exceptions import ex as mEx  # noqa: N812
from .tbl_data_obj import TblDataObj

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class AutoFn:
    """Class that generates the lp function"""

    def __init__(self, cell_rng: CalcCellRange, orig_sheet_idx: int) -> None:
        """
        Constructor

        Args:
            cell_rng (CalcCellRange): The cell range to get the table information from.
        """
        self._log = OxtLogger(log_name=self.__class__.__name__)
        if self._log.is_debug:
            self._log.debug(f"init cell range: {cell_rng.range_obj}, Original Sheet Index: {orig_sheet_idx}")
        self._cell_rng = cell_rng
        self._orig_sheet_idx = orig_sheet_idx
        self._data_info = TblDataObj(cell_rng)
        self._log.debug("init complete.")

    def generate_fn(self) -> str:
        """Generates the lp function"""
        self._log.debug("generate_fn() Entered")

        s = ""
        if self._cell_rng.range_obj.is_single_cell():
            if self._orig_sheet_idx == self._cell_rng.range_obj.sheet_idx:
                s += f'lp("{self._cell_rng.range_obj.cell_start}")'
            else:
                s += f'lp("{self._cell_rng.range_obj.cell_start.to_string(True)}")'
            # single cell return the value
            self._log.debug(f"generate_fn() returning '{s}'")
            return s
        else:
            if self._orig_sheet_idx == self._cell_rng.range_obj.sheet_idx:
                s += f'lp("{self._cell_rng.range_obj}"'
            else:
                s += f'lp("{self._cell_rng.range_obj.to_string(True)}"'
        if self._data_info.has_headers:
            # headers = self._data_info.headers
            s += ", headers=True"
        if self._get_include_collapse():
            s += ", collapse=True"
        s += ")"

        self._log.debug(f"generate_fn() returning '{s}'")
        return s

    def _get_include_collapse(self) -> bool:
        """Determines if the collapse parameter should be included"""
        ro_orig = self._cell_rng.range_obj
        try:
            ro = self._cell_rng.find_used_range()
            if ro_orig != ro.range_obj:
                return True
        except mEx.CellRangeError:
            self._log.debug("Error getting used range. Find used range did not get a value. Not critical.")
        except Exception as e:
            self._log.exception(f"Error: {e}")
        return False
