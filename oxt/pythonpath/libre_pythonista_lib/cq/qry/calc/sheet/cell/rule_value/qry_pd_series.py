from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Iterable
from collections import OrderedDict

import pandas as pd
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.pandas_util import PandasUtil
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_state import QryState
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state.state_kind import StateKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.pandas_util import PandasUtil
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_py_src.py


class QrySeries(QryBase, LogMixin, QryCellT[Result[Iterable[Iterable[object]], None] | Result[None, Exception]]):
    """
    Query class for handling pandas Series data in LibreOffice Calc cells.

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

    def _qry_state(self) -> Result[StateKind, None] | Result[None, Exception]:
        """
        Query the state of the cell.

        Returns:
            Result: Success contains StateKind, Failure contains Exception
        """
        qry = QryState(cell=self._cell)
        return self._execute_qry(qry)

    def _pandas_to_array(self) -> Any:  # noqa: ANN401
        """
        Convert pandas Series to a 2D array format compatible with LibreOffice Calc.

        Handles date series specially by converting dates to LibreOffice format.
        If series has a name, adds it as a header row.

        Returns:
            list: 2D array containing the converted Series data
        """
        ds = cast(pd.Series, self._data.data)
        if PandasUtil.is_date_series(ds):
            ds_copy = ds.copy()
            PandasUtil.pandas_series_to_lo_calc(ds_copy)
            d = ds_copy.to_dict(into=OrderedDict)
        else:
            d = ds.to_dict(into=OrderedDict)

        d = PandasUtil.convert_dict_keys_to_lo_date(d)

        list_2d = [[k, v] for k, v in d.items()]
        if ds.name:
            list_2d.insert(0, ["", ds.name])
        return list_2d

    def execute(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        """
        Execute the query to convert pandas Series data for LibreOffice Calc.

        Returns:
            Result: Success contains converted array data or empty tuple,
                Failure contains Exception
        """
        try:
            state = self._qry_state()
            if Result.is_failure(state):
                return state
            if state.data == StateKind.ARRAY:
                return Result.success(self._pandas_to_array())
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
