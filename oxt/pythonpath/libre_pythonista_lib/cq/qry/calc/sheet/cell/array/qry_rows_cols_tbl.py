from __future__ import annotations

from typing import Any, cast, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_module_state import QryModuleState
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

    PyModuleT = Any


class QryRowsColsTbl(QryBase, LogMixin, QryCellT[Union[Result[List[int], None], Result[None, Exception]]]):
    """
    Query that returns the number of rows and columns in a Data Table associated with a cell.

    Args:
        cell (CalcCell): The cell to query
        mod (PyModuleT, None): Optional Python module. If None, will be queried using QryPyModuleDefault
    """

    def __init__(self, cell: CalcCell, mod: Union[PyModuleT, None] = None) -> None:
        """
        Initialize the query with a cell and optional module.

        Args:
            cell (CalcCell): The cell to query
            mod (PyModuleT, None, optional): Optional Python module. If None, will be queried using QryPyModuleDefault. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = cast(PyModuleT, mod)
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_mod(self) -> PyModuleT:
        """Gets the Python module via query"""
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def _qry_module_state(self) -> ModuleStateItem:
        """
        Queries the current module state for the cell

        Returns:
            ModuleStateItem: The module state for the cell

        Raises:
            Exception: If query fails
        """
        qry = QryModuleState(cell=self._cell, mod=self._mod)
        result = self._execute_qry(qry)

        if Result.is_success(result):
            return result.data
        raise result.error

    def _get_rows_cols(self, module_item: ModuleStateItem) -> List[int]:
        """
        Gets the number of rows and columns for a Data Table.

        Args:
            module_item (ModuleStateItem): The module state containing Data Table data

        Returns:
            List[int]: A list containing [num_rows, num_cols]
        """
        lst_data = cast(List[List[Any]], module_item.dd_data.data)
        rows = len(lst_data)
        if rows == 0:
            return [0, 0]
        first = lst_data[0]
        cols = len(first)
        return [rows, cols]

    def execute(self) -> Union[Result[List[int], None], Result[None, Exception]]:
        """
        Executes the query to get DataFrame dimensions.

        Returns:
            Result: Success with [num_rows, num_cols] or Failure with Exception
        """
        if self._mod is None:
            self._mod = self._qry_mod()
        try:
            module_item = self._qry_module_state()
            result = self._get_rows_cols(module_item)
            return Result.success(result)
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """The cell being queried"""
        return self._cell
