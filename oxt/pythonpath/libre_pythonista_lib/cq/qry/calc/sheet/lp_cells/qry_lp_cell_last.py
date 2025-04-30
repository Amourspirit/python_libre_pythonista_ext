from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_obj_list import QryLpCellObjList
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cells_by_sheet import QryLpCellsBySheet
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_obj_list import QryLpCellObjList
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryLpCellLast(QryBase, LogMixin, QrySheetT[Result[CellObj, None] | Result[None, Exception]]):
    """
    Query to get the last LibrePythonista cell in a sheet.

    Args:
        sheet (CalcSheet): The sheet to query.
        from_sheet (bool, optional): If True, gets cells directly from sheet. If False, gets from Python source manager. Defaults to False.
    """

    def __init__(self, sheet: CalcSheet, from_sheet: bool = False) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._sheet = sheet
        self._from_sheet = from_sheet
        self.log.debug("init done for doc %s", sheet.name)

    def _qry_lp_cells_by_sheet(self) -> Dict[CellObj, IndexCellProps]:
        """
        Get all LibrePythonista cells in the sheet.

        Returns:
            Dict[CellObj, IndexCellProps]: Dictionary mapping cells to their properties.

        Raises:
            Exception: If query fails.
        """
        qry = QryLpCellsBySheet(sheet=self._sheet)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_lp_cell_obj_list(self) -> List[CellObj]:
        """
        Get all LibrePythonista cells in the sheet.

        Returns:
            List[CellObj]: List of cells.

        Raises:
            Exception: If query fails.
        """
        qry = QryLpCellObjList(sheet=self._sheet)
        return self._execute_qry(qry)

    def _execute_from_py_src_mgr(self) -> Result[CellObj, None] | Result[None, Exception]:
        """
        Execute query using Python source manager.

        Returns:
            Result: Success with last CellObj or Failure with None/Exception.
        """
        try:
            sheet_cells = self._qry_lp_cells_by_sheet()
            if len(sheet_cells) == 0:
                self.log.error("get_last_cell() No cells in sheet")
                return Result.failure(Exception("No cells in sheet"))

            # return last item in sheet_cells
            return Result.success(next(reversed(sheet_cells)))
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)

    def _execute_from_sheet(self) -> Result[CellObj, None] | Result[None, Exception]:
        """
        Execute query directly from sheet.

        Returns:
            Result: Success with last CellObj or Failure with None/Exception.
        """
        try:
            sheet_cells = self._qry_lp_cell_obj_list()
            if len(sheet_cells) == 0:
                self.log.error("get_last_cell() No cells in sheet")
                return Result.failure(Exception("No cells in sheet"))

            # return last item in sheet_cells
            return Result.success(sheet_cells[-1])
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)

    def execute(self) -> Result[CellObj, None] | Result[None, Exception]:
        """
        Execute the query to get the last cell.

        Returns:
            Result: Success with last CellObj or Failure with None/Exception.
        """
        if self._from_sheet:
            return self._execute_from_sheet()
        return self._execute_from_py_src_mgr()

    @property
    def sheet(self) -> CalcSheet:
        """The sheet being queried."""
        return self._sheet
