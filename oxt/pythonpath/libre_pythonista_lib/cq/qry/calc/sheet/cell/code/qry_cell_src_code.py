from __future__ import annotations


from typing import TYPE_CHECKING, Union
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_uri import QryCellUri
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySource
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryCellSrcCode(QryBase, LogMixin, QryCellT[Union[Result[str, None], Result[None, Exception]]]):
    """Gets the source code for a cell"""

    def __init__(self, cell: CalcCell, uri: str = "") -> None:
        """Constructor

        Args:
            uri (str, optional): URI of the source code.
                if not provided then it will be queried. Defaults to "".
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._uri = uri
        self._cell = cell
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_cell_uri(self) -> str:
        """Get the URI identifier for the cell."""
        qry = QryCellUri(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def execute(self) -> Union[Result[str, None], Result[None, Exception]]:
        """
        Executes the query to get the cell source code.

        Returns:
            Result: Success with source code or Failure with Exception
        """

        try:
            if not self._uri:
                self._uri = self._qry_cell_uri()
            py_code = PySource(uri=self._uri, cell=self.cell.cell_obj)
            if not py_code.exists():
                return Result.failure(ValueError("Source code does not exits"))
            return Result.success(py_code.source_code)
        except Exception:
            self.log.exception("Error executing query")
        return Result.failure(Exception("Source code not found"))

    @property
    def cell(self) -> CalcCell:
        return self._cell
