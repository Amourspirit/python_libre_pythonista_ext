from __future__ import annotations

from typing import cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.array.qry_rows_cols_tbl import QryRowsColsTbl
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.utils.custom_ext import override


class QryRowsColsPdDf(QryRowsColsTbl):
    """
    Query that returns the number of rows and columns in a Pandas DataFrame associated with a cell.

    Args:
        cell (CalcCell): The cell to query
        mod (PyModuleT | None): Optional Python module. If None, will be queried using QryPyModuleDefault
    """

    @override
    def _get_rows_cols(self, module_item: ModuleStateItem) -> List[int]:
        """
        Gets the number of rows and columns for a Pandas DataFrame.

        Returns:
            List[int]: A list containing [num_rows, num_cols]
        """
        if TYPE_CHECKING:
            import pandas as pd
            from oxt.pythonpath.libre_pythonista_lib.utils.pandas_util import PandasUtil
        else:
            from libre_pythonista_lib.utils.pandas_util import PandasUtil

        df = cast("pd.DataFrame", module_item.dd_data.data)
        has_headers = bool(module_item.dd_data.get("headers", False))
        if has_headers is False:
            has_headers = PandasUtil.has_headers(df)
        has_index_names = PandasUtil.has_index_names(df)
        if self.log.is_debug:
            self.log.debug("get_rows_cols() - Has Headers: %s", has_headers)
            self.log.debug("get_rows_cols() - Has Index Names: %s", has_index_names)

        if self.log.is_debug:
            self.log.debug("DataFrame Shape: %s", df.shape)
        shape = df.shape
        shape_len = len(shape)
        lst = [0, 0]
        if shape_len == 0:
            return lst

        if shape_len == 1:
            lst[0] = shape[0]
        else:
            lst[0] = shape[0]
            lst[1] = shape[1]
        if has_headers:
            lst[0] += 1

        if has_index_names:
            lst[1] += 1
        return lst
