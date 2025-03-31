from __future__ import annotations
from typing import Any, Iterable, Tuple, TYPE_CHECKING

from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_empty import QryEmpty
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_direct_data import QryDirectData
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_tbl_data import QryTblData
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_empty import QryEmpty
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_direct_data import QryDirectData
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_tbl_data import QryTblData
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryValue(QryBase, LogMixin, QryCellT[Result[Iterable[Iterable[object]], None] | Result[None, Exception]]):
    def __init__(self, cell: CalcCell, rule_kind: RuleNameKind, data: DotDict) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._rule_kind = rule_kind
        self._data = data

    def qry_empty(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        qry = QryEmpty(data=self._data)
        return self._execute_qry(qry)

    def qry_direct_data(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        qry = QryDirectData(data=self._data)
        return self._execute_qry(qry)

    def qry_pd_df(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_pd_df import QryPdDf
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_pd_df import QryPdDf
        qry = QryPdDf(cell=self._cell, data=self._data)
        return self._execute_qry(qry)

    def qry_pd_series(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_pd_series import QrySeries
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_pd_series import QrySeries
        qry = QrySeries(cell=self._cell, data=self._data)
        return self._execute_qry(qry)

    def qry_tbl_data(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        qry = QryTblData(cell=self._cell, data=self._data)
        return self._execute_qry(qry)

    def execute(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        """
        Executes the query to get the URI for a cell.

        In format of ``vnd.sun.star.tdoc:/1/librepythonista/sheet_unique_id_bla_bla/code_name_bla_bal.py``

        Returns:
            Result: Success with URI or Failure with Exception
        """
        try:
            self.log.debug("execute() - rule_kind: %s", self._rule_kind)
            if self._rule_kind in (
                RuleNameKind.CELL_DATA_TYPE_EMPTY,
                RuleNameKind.CELL_DATA_TYPE_NONE,
                RuleNameKind.CELL_DATA_TYPE_ERROR,
                RuleNameKind.CELL_DATA_TYPE_MP_FIGURE,
            ):
                return self.qry_empty()
            if self._rule_kind in (
                RuleNameKind.CELL_DATA_TYPE_FLOAT,
                RuleNameKind.CELL_DATA_TYPE_INT,
                RuleNameKind.CELL_DATA_TYPE_STR,
            ):
                return self.qry_direct_data()
            if self._rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_DF:
                self.log.debug("execute() -Success for rule_kind: %s", self._rule_kind)
                return self.qry_pd_df()
            if self._rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_SERIES:
                self.log.debug("execute() -Success for rule_kind: %s", self._rule_kind)
                return self.qry_pd_series()
            if self._rule_kind == RuleNameKind.CELL_DATA_TYPE_TBL_DATA:
                self.log.debug("execute() -Success for rule_kind: %s", self._rule_kind)
                return self.qry_tbl_data()
            self.log.error("Not implemented rule kind: %s", self._rule_kind)
            return Result.failure(NotImplementedError("Not implemented rule kind: %s", self._rule_kind))
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        return self._cell
