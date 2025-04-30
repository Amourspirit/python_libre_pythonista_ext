from __future__ import annotations
from typing import Iterable, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryTblData(QryBase, LogMixin, QryCellT[Result[Iterable[Iterable[object]], None] | Result[None, Exception]]):
    """
    Query class for handling table data in LibreOffice Calc cells.

    Inherits from QryBase, LogMixin, and QryCellT with a Result type that can contain
    either Any data or an Exception.
    """

    def __init__(self, cell: CalcCell, data: DotDict) -> None:
        """
        Initialize a new QrySeries instance.

        Args:
            cell (CalcCell): The LibreOffice Calc cell to query
            data (DotDict): Data containing a pandas Series to process
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._data = data
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_state(self) -> Result[StateKind, None] | Result[None, Exception]:
        """
        Query the state of the cell.

        Returns:
            Result: Success contains StateKind, Failure contains Exception
        """
        qry = QryState(cell=self._cell)
        return self._execute_qry(qry)

    def execute(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        """
        Execute the query to convert table data for LibreOffice Calc.

        Returns:
            Result: Success contains converted array data or empty tuple,
                Failure contains Exception
        """
        try:
            state = self._qry_state()
            if Result.is_failure(state):
                return state
            if state.data == StateKind.ARRAY:
                return Result.success(self._data.data)
            else:
                return Result.success((("",),))
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """
        Get the target cell.

        Returns:
            CalcCell: The LibreOffice Calc cell being queried
        """
        return self._cell
