from __future__ import annotations


from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import CELL_PY_SOURCE
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const.cache_const import CELL_PY_SOURCE
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache_t import QryCellCacheT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

    PySrcProvider = Any


class QryCellPySource(QryBase, LogMixin, QryCellCacheT[PySource]):
    """Gets the PySource for a cell"""

    def __init__(self, uri: str, cell: CalcCell, src_provider: PySrcProvider | None = None) -> None:
        """Constructor

        Args:
            uri (str): URI of the source code.
            cell (CalcCell): Cell to query.
            src_provider (PySrcProvider, optional): Source provider. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL_CACHE
        self._uri = uri
        self._cell = cell
        self._src_provider = src_provider

    def execute(self) -> PySource:
        """Executes the query to get the PySource"""
        return PySource(uri=self._uri, cell=self.cell.cell_obj, src_provider=self._src_provider)

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return CELL_PY_SOURCE
