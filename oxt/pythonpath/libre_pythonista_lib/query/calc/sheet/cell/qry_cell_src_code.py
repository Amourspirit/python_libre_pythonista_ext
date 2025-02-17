from __future__ import annotations


from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.pyc.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_SRC_CODE
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.pyc.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const.cache_const import CELL_SRC_CODE
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT

    PySrcProvider = Any

# call with QryHandlerCellCache
# from libre_pythonista_lib.query.calc.sheet.cell.qry_handler_cell_cache import QryHandlerCellCache


class QryCellSrcCode(LogMixin, QryCellCacheT):
    def __init__(self, uri: str, cell: CalcCell, src_provider: PySrcProvider | None = None) -> None:
        LogMixin.__init__(self)
        self._uri = uri
        self._cell = cell
        self._src_provider = src_provider

    def execute(self) -> str | None:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        try:
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj, src_provider=self._src_provider)
            return py_code.source_code
        except Exception:
            self.log.exception("Error executing query")
        return None

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return CELL_SRC_CODE
