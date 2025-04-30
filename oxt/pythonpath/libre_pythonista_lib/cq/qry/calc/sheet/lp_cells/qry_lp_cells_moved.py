from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcSheet, CalcCell
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELLS_MOVED
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_last import QryLpCellLast
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.const.cache_const import CELLS_MOVED
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.lp_cells.qry_lp_cell_last import QryLpCellLast
    from libre_pythonista_lib.utils.result import Result


class QryLpCellsMoved(QryBase, LogMixin, QrySheetCacheT[bool]):
    """
    Query to check if cells containing Python code have been moved in a sheet.

    Inherits from QryBase, LogMixin, and QrySheetCacheT[bool].
    """

    def __init__(self, sheet: CalcSheet, mod: PyModuleT | None = None) -> None:
        """
        Initialize the query.

        Args:
            sheet: The CalcSheet to check for moved cells
            mod: Optional PyModuleT to filter which cells to check
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET_CACHE
        self._mod = mod
        self._sheet = sheet
        self.log.debug("init done for sheet %s", sheet.name)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Gets the Python source manager via query.

        Returns:
            PySourceManager: The source manager for the sheet's document
        """
        qry = QryPySrcMgr(doc=self._sheet.calc_doc, mod=self._mod)
        return self._execute_qry(qry)

    def _qry_address(self, cell: CalcCell) -> Addr | None:
        """
        Query the address of a cell.

        Args:
            cell: The CalcCell to get the address for

        Returns:
            Addr | None: The cell's address or None if query fails
        """
        qry = QryAddr(cell=cell)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        self.log.debug("_qry_address() Address not found")
        return None

    def _qry_lp_cell_last(self) -> CellObj | None:
        """
        Query the last Python source cell in the sheet.

        Returns:
            CellObj: The last source cell's object
        """
        qry = QryLpCellLast(sheet=self._sheet, from_sheet=True)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    def _get_last_cell(self) -> PySource | None:
        """
        Get the last Python source cell from the source manager.

        Returns:
            PySource | None: The last source cell or None if none exists
        """
        mgr = self._qry_py_src_mgr()
        return mgr.get_last_item()

    def _is_moved(self) -> bool:
        """
        Check if the last Python source cell has moved.

        Returns:
            bool: True if the cell has moved, False otherwise
        """
        last = self._get_last_cell()
        if last is None:
            self.log.debug("_is_moved() No last cell found")
            return False
        last_sheet = self._qry_lp_cell_last()
        if last_sheet is None:
            self.log.debug("_is_moved() No last cell found")
            return False
        return last_sheet != last.cell_obj

    def execute(self) -> bool:
        """
        Execute the query to check if cells have moved.

        Returns:
            bool: True if cells have moved, False otherwise or on error
        """
        try:
            moved = self._is_moved()
            self.log.debug("execute() Cells moved: %s", moved)
            return moved
        except Exception as e:
            self.log.exception("Error executing query: %s", e)
            return False

    @property
    def cache_key(self) -> str:
        """
        Gets the cache key.

        Returns:
            str: The cache key for this query
        """
        return CELLS_MOVED

    @property
    def sheet(self) -> CalcSheet:
        """
        Gets the sheet being queried.

        Returns:
            CalcSheet: The sheet instance this query operates on
        """
        return self._sheet
