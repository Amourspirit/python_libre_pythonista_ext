from __future__ import annotations

from typing import TYPE_CHECKING, cast, Dict, Tuple, Union
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_managed_cache_t import QrySheetManagedCacheT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.const import PYTHON_SOURCE_MODIFIED
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_managed_cache_t import QrySheetManagedCacheT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.doc.calc.const import PYTHON_SOURCE_MODIFIED
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


# see cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet.QryLpCellsBySheet


class QryLpCellsBySheet(
    QryBase,
    LogMixin,
    QrySheetManagedCacheT[Union[Result[Dict[CellObj, IndexCellProps], None], Result[None, Exception]]],
):
    """
    Query that retrieves cells and their properties for a specific sheet in a Calc document.
    Returns a dictionary mapping cell objects to their index properties.

    Note:
        The return value is sorted by CellObj.
    """

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Initialize the query.

        Args:
            sheet (CalcSheet): The sheet to query
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET_MANAGED_CACHE
        self._sheet = sheet
        self.log.debug("init done for doc %s", sheet.name)

    def _qry_cell_cp_code_name(self) -> str:
        """
        Query class that retrieves the codename from configuration.
        Something like ``libre_pythonista_codename``

        Returns:
            str: The codename used for filtering cells.
        """
        qry = QryCellCpCodeName()
        return self._execute_qry(qry)

    def _get_cells(self) -> Dict[CellObj, IndexCellProps]:
        """
        Gets all cells with custom properties matching the code name filter.

        Returns:
            Dict[CellObj, IndexCellProps]: Dictionary mapping cells to their index properties
        """
        filter_key = self._qry_cell_cp_code_name()
        sheet = self._sheet

        code_index: Dict[CellObj, IndexCellProps] = {}
        # deleted cells will not be in the custom properties

        code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)
        i = -1
        for key, value in code_cell.items():
            i += 1
            cell = sheet[key]
            code_name = cast(str, cell.get_custom_property(filter_key, ""))
            if not code_name:
                self.log.error("_get_cells() Code Name not found for cell: %s. Skipping?", cell)
                continue
            code_index[key] = IndexCellProps(code_name, value, i)
        return code_index

    def execute(self) -> Union[Result[Dict[CellObj, IndexCellProps], None], Result[None, Exception]]:
        """
        Executes the query to get cells and their properties.

        Returns:
            Result: Success with Dict[CellObj, IndexCellProps] or Failure with Exception
        """
        try:
            return Result.success(self._get_cells())
        except Exception:
            self.log.exception("Error executing query")
        return Result.failure(Exception("Error executing query"))

    @property
    def sheet(self) -> CalcSheet:
        """Gets the sheet being queried."""
        return self._sheet

    @property
    def cache_key_events(self) -> Tuple[str, Tuple[str, ...]]:
        """
        Gets the cache key and event names.

        Returns:
            Tuple[str, Tuple[str, ...]]: A tuple containing the cache key and a tuple of event names
        """
        return (
            "libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet.QryLpCellsBySheet",
            (PYTHON_SOURCE_MODIFIED,),
        )
