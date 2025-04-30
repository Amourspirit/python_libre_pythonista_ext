from __future__ import annotations

from typing import Any, cast, TYPE_CHECKING, Iterable
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


class QryPdDf(QryBase, LogMixin, QryCellT[Result[Iterable[Iterable[object]], None] | Result[None, Exception]]):
    """
    Query class for converting Pandas DataFrame data to a format suitable for LibreOffice Calc.

    This class handles the conversion of Pandas DataFrame data to array format that can be used in LibreOffice Calc cells.
    It checks the cell's state and performs appropriate conversions based on whether the data represents a describe output
    or regular DataFrame.

    Args:
        cell (CalcCell): The target cell in LibreOffice Calc.
        data (DotDict): Data containing the Pandas DataFrame to be converted.
    """

    def __init__(self, cell: CalcCell, data: DotDict) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
            data (DotDict): Data to query.
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
            Result containing the StateKind if successful, or Exception if failed.
        """
        qry = QryState(cell=self._cell)
        return self._execute_qry(qry)

    def _df_headers_to_array(self) -> Any:  # noqa: ANN401
        """
        Convert Pandas DataFrame to an array format suitable for LibreOffice.

        Returns:
            Any: Array representation of DataFrame, with special handling for describe() output
        """
        df = cast(pd.DataFrame, self._data.data)
        if not isinstance(df, pd.DataFrame):
            self.log.warning(
                "_df_headers_to_array() Data is not a DataFrame for cell: %s. Expected DataFrame got %s",
                self._cell.cell_obj,
                type(df).__name__,
            )
            return []
        if PandasUtil.is_describe_output(df):
            arr = PandasUtil.pandas_to_array(df, header_opt=1, index_opt=0, convert=False)
            PandasUtil.convert_array_to_lo(arr)
            return arr
        return PandasUtil.pandas_to_array(df, header_opt=1, index_opt=0)

    def _df_to_array(self) -> Any:  # noqa: ANN401
        """
        Convert Pandas DataFrame to array format suitable for LibreOffice Calc.

        Handles both describe output and regular DataFrames differently.
        For describe output, preserves the original format without conversion.
        For regular DataFrames, converts to standard array format.

        Returns:
            Array format data suitable for LibreOffice Calc.
        """
        df = cast(pd.DataFrame, self._data.data)
        if not isinstance(df, pd.DataFrame):
            self.log.warning(
                "_df_to_array() Data is not a DataFrame for cell: %s. Expected DataFrame got %s",
                self._cell.cell_obj,
                type(df).__name__,
            )
            return []
        if PandasUtil.is_describe_output(df):
            arr = PandasUtil.pandas_to_array(df, convert=False)
            PandasUtil.convert_array_to_lo(arr)
            return arr
        return PandasUtil.pandas_to_array(df)

    def execute(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        """
        Execute the query to convert Pandas DataFrame to LibreOffice Calc format.

        Checks cell state and performs appropriate conversion based on state.
        Returns empty tuple (("",),) if cell is not in ARRAY state.

        Returns:
            Result containing converted array data if successful, or Exception if failed.
        """
        try:
            state = self._qry_state()
            if Result.is_failure(state):
                return state
            if state.data == StateKind.ARRAY:
                headers = bool(self._data.get("headers", False))
                if headers:
                    return Result.success(self._df_headers_to_array())
                return Result.success(self._df_to_array())
            else:
                return Result.success((("",),))
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """
        Get the target cell.

        Returns:
            CalcCell: The LibreOffice Calc cell being queried.
        """
        return self._cell
