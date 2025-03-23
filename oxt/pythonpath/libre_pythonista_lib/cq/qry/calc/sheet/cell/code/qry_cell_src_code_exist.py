from __future__ import annotations


from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE_EXIST
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE_EXIST
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryCellSrcCodeExist(QryBase, LogMixin, QryCellCacheT[bool]):
    """Checks if the source code exists for a cell"""

    def __init__(self, uri: str, cell: CalcCell) -> None:
        """Constructor

        Args:
            uri (str): URI of the source code.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL_CACHE
        self._uri = uri
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query and gets if the source code exists.

        Returns:
            bool: True if the source code exists, False otherwise.
        """

        try:
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj)
            return py_code.exists()
        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return CELL_SRC_CODE_EXIST
