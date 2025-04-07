from __future__ import annotations

from typing import TYPE_CHECKING, cast, Dict
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
    from libre_pythonista_lib.utils.result import Result


class QryLpCellsBySheet(
    QryBase, LogMixin, QrySheetT[Result[Dict[CellObj, IndexCellProps], None] | Result[None, Exception]]
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
            doc (CalcDoc): The Calc document to query
            sheet_idx (int): Index of the sheet to query
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
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
        index = sheet.sheet_index
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

    def execute(self) -> Result[Dict[CellObj, IndexCellProps], None] | Result[None, Exception]:
        """
        Executes the query to get cells and their properties.

        Returns:
            Dict[CellObj, IndexCellProps]: Dictionary mapping cells to their index properties.
            Returns empty dict if execution fails.
        """
        try:
            return Result.success(self._get_cells())
        except Exception:
            self.log.exception("Error executing query")
        return Result.failure(Exception("Error executing query"))

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
