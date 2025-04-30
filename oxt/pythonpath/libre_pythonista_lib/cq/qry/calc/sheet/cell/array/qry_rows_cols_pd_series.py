from __future__ import annotations

from typing import cast, List, TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_value import QryValue
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.rule_value.qry_value import QryValue
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.utils.result import Result


class QryRowsColsPdSeries(QryRowsColsTbl):
    """
    Query that returns the number of rows and columns in a Pandas Series associated with a cell.

    Args:
        cell (CalcCell): The cell to query
        mod (PyModuleT | None): Optional Python module. If None, will be queried using QryPyModuleDefault
    """

    def _qry_ctl_rule_name_kind(self) -> RuleNameKind:
        """Queries the rule name kind for the cell's control"""
        qry = QryPycRule(self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            self.log.debug("qry_ctl_rule_name_kind_result: %s for cell: %s", result.data, self.cell.cell_obj)
            return result.data
        raise result.error

    def _qry_value(self) -> Iterable[Iterable[object]]:
        """Queries the value of the cell"""
        rule_kind = self._qry_ctl_rule_name_kind()
        state = self._qry_module_state()
        qry = QryValue(cell=self.cell, rule_kind=rule_kind, data=state.dd_data)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        raise result.error

    @override
    def _get_rows_cols(self, module_item: ModuleStateItem) -> List[int]:
        """
        Gets the number of rows and columns for a Pandas Series.

        Returns:
            List[int]: A list containing [num_rows, num_cols]
        """
        if TYPE_CHECKING:
            import pandas as pd

        s = cast("pd.Series", self._qry_value())
        series_len = len(s)
        if not series_len:
            return [0, 0]
        if s.name:
            return [series_len + 1, 2]
        return [series_len, 2]
