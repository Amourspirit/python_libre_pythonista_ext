from __future__ import annotations

from typing import Any, cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind

    PyModuleT = Any


class QryRowCols(QryBase, LogMixin, QryCellT[Result[List[int], None] | Result[None, Exception]]):
    """
    Query that returns the number of rows and columns in a Data Table associated with a cell.

    Args:
        cell (CalcCell): The cell to query
        mod (PyModuleT | None): Optional Python module. If None, will be queried using QryPyModuleDefault
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None) -> None:
        """
        Initialize the query with a cell and optional module.

        Args:
            cell (CalcCell): The cell to query
            mod (PyModuleT | None, optional): Optional Python module. If None, will be queried using QryPyModuleDefault. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = cast(PyModuleT, mod)
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_rule_kind(self) -> RuleNameKind:
        """Queries the rule kind for the cell"""
        qry = QryPycRule(self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_rows_cols_tbl(self) -> List[int]:
        """Queries the number of rows and columns for a Data Table"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import (
                QryRowsColsTbl,
            )
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl

        qry = QryRowsColsTbl(cell=self.cell, mod=self._mod)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_rows_cols_pd_df(self) -> List[int]:
        """Queries the number of rows and columns for a Pandas DataFrame"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_pd_df import (
                QryRowsColsPdDf,
            )
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_pd_df import QryRowsColsPdDf

        qry = QryRowsColsPdDf(cell=self.cell, mod=self._mod)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_rows_cols_pd_series(self) -> List[int]:
        """Queries the number of rows and columns for a Pandas Series"""
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_pd_series import (
                QryRowsColsPdSeries,
            )
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_pd_series import QryRowsColsPdSeries
        qry = QryRowsColsPdSeries(cell=self.cell, mod=self._mod)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    def _qry_mod(self) -> PyModuleT:
        """Gets the Python module via query"""
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def execute(self) -> Result[List[int], None] | Result[None, Exception]:
        """
        Executes the query to get DataFrame dimensions.

        Returns:
            Result: Success with [num_rows, num_cols] or Failure with Exception
        """
        if self._mod is None:
            self._mod = self._qry_mod()
        try:
            kind = self._qry_rule_kind()
            if kind == RuleNameKind.CELL_DATA_TYPE_PD_DF:
                return Result.success(self._qry_rows_cols_pd_df())
            if kind == RuleNameKind.CELL_DATA_TYPE_PD_SERIES:
                return Result.success(self._qry_rows_cols_pd_series())
            if kind == RuleNameKind.CELL_DATA_TYPE_TBL_DATA:
                return Result.success(self._qry_rows_cols_tbl())
            return Result.failure(NotImplementedError("Not implemented rule kind: %s", kind))
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """The cell being queried"""
        return self._cell
