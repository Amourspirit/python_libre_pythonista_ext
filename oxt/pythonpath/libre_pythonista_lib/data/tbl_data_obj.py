from __future__ import annotations
from typing import cast, List, Tuple, TYPE_CHECKING
from com.sun.star.table import CellRangeAddress
from com.sun.star.sheet import CellFlags  # const
from ooodev.calc import CalcCellRange, RangeObj

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class TblDataObj:
    """Class that gets table information on a cell range."""

    def __init__(self, cell_rng: CalcCellRange):
        """
        Constructor

        Args:
            cell_rng (CalcCellRange): The cell range to get the table information from.
        """
        self._log = OxtLogger(log_name=self.__class__.__name__)
        if self._log.is_debug:
            self._log.debug(f"init: {cell_rng.range_obj}")
        self._sheet = cell_rng.calc_sheet
        self._doc = cell_rng.calc_doc
        self._cell_rng = cell_rng
        self._date_columns = None
        self._headers = None
        self._log.debug("init complete.")

    def _rng_has_header(self) -> List[str]:
        """
        Check if the range has headers. Considered to be a header if the first row is all string values.

        Returns:
            bool: True if the range has headers.
        """
        # Check of the first row is all string values.
        # If there are merged cell in the header then the number of ranges will be more than 1
        # which will return False.
        self._log.debug("_rng_has_header() Entered")
        ro = self._cell_rng.range_obj
        if ro.is_single_row():
            self._log.debug("_rng_has_header() Single row detected, returning Headers: []")
            return []
        start_ro = ro.get_start_row()
        calc_rng = self._cell_rng.calc_sheet.get_range(range_obj=start_ro)
        cursor = calc_rng.create_cursor()
        ranges = cursor.component.queryContentCells(CellFlags.STRING)
        if len(ranges.RangeAddresses) != 1:  # type: ignore
            self._log.debug("_rng_has_header() Multiple ranges detected, returning Headers: []")
            return []
        cra = cast(CellRangeAddress, ranges.RangeAddresses[0])  # type: ignore
        found_rng = RangeObj.from_range(cra)
        if self._log.is_debug:
            self._log.debug(f"_rng_has_header() Found Range: {found_rng}")
        if found_rng != start_ro:
            self._log.debug("_rng_has_header() Found Range does not match start row, returning Headers: []")
            return []
        arr = self._sheet.get_array(range_obj=found_rng)
        if self._log.is_debug:
            self._log.debug(f"_rng_has_header() returning Headers: {list(arr[0])}")
        return list(arr[0])

    def _get_date_columns(self) -> List[int]:
        """
        Queries all constant numeric values that have a date or time number format.
        Checks the queries to see if they match entire columns.
        Match columns are returned as a list of zero-based column indexes.

        Returns:
            List[int]: A list of zero-based column indexes that contain date values.
        """
        self._log.debug("_get_date_columns() Entered")
        ro = self._cell_rng.range_obj
        if self.has_headers:
            # skip the header row
            # https://tinyurl.com/2zswb49z#subtracting-rows-using-integer
            ro = 1 - ro

        calc_rng = self._sheet.get_range(range_obj=ro)
        rv = ro.get_range_values()
        cursor = calc_rng.create_cursor()
        ranges = cursor.component.queryContentCells(CellFlags.DATETIME)
        cra_vals = cast(Tuple[CellRangeAddress, ...], ranges.RangeAddresses)  # type: ignore
        if self._log.is_debug:
            self._log.debug(f"_get_date_columns() Range Value Count: {len(cra_vals)}")
        if len(cra_vals) == 0:  # type: ignore
            return []
        date_columns = []
        for cra in cra_vals:  # type: ignore
            if cra.StartColumn != cra.EndColumn:
                # must be a single column
                continue
            # check to see if the column spans the entire range
            if cra.StartRow == rv.row_start and cra.EndRow == rv.row_end:
                date_columns.append(cra.StartColumn)
        if self._log.is_debug:
            self._log.debug(f"_get_date_columns() returning Date Columns: {date_columns}")
        return date_columns

    def get_date_column_names(self) -> List[str]:
        """Gets the names of the columns that contain date values."""
        col_names = [self.headers[i] for i in self.date_columns]
        if self._log.is_debug:
            self._log.debug(f"get_date_column_names() returning Date Column Names: {col_names}")
        return col_names

    # region Properties
    @property
    def col_count(self) -> int:
        """Gets the number of columns in the range."""
        start_idx = self._cell_rng.range_obj.start_col_index
        end_idx = self._cell_rng.range_obj.end_col_index
        return end_idx - start_idx + 1

    @property
    def headers(self) -> List[str]:
        """Gets the headers of the range."""
        if self._headers is None:
            self._headers = self._rng_has_header()
        return self._headers

    @property
    def has_headers(self) -> bool:
        """
        Check if the range has headers.

        Headers are considered to be True if the first row is all string values.
        """
        return len(self.headers) > 0

    @property
    def date_columns(self) -> List[int]:
        """Gets the zero-based column indexes that contain date values."""
        if self._date_columns is None:
            self._date_columns = self._get_date_columns()
        return self._date_columns

    @property
    def has_date_columns(self) -> bool:
        """Check if the range has date columns."""
        return len(self.date_columns) > 0

    # endregion Properties
