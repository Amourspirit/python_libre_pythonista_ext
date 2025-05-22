from __future__ import annotations

from typing import cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from libre_pythonista_lib.utils.custom_ext import override


class QryRowsColsPdSeries(QryRowsColsTbl):
    """
    Query that returns the number of rows and columns in a Pandas Series associated with a cell.

    Args:
        cell (CalcCell): The cell to query
        mod (PyModule, None): Optional Python module. If None, will be queried using QryPyModuleDefault
    """

    @override
    def _get_rows_cols(self, module_item: ModuleStateItem) -> List[int]:
        """
        Gets the number of rows and columns for a Pandas Series.

        Returns:
            List[int]: A list containing [num_rows, num_cols]
        """
        if TYPE_CHECKING:
            import pandas as pd

        # s = cast("pd.Series", self._qry_value())
        s = cast("pd.Series", module_item.dd_data.data)
        series_len = len(s)
        if not series_len:
            return [0, 0]
        if s.name:
            return [series_len + 1, 2]
        return [series_len, 2]
