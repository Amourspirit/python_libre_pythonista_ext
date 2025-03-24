from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.utils.result import Result

    PySourceManager = Any

# The state item must be gotten from the source manager.
# Otherwise, the source manager may not be initialized.
# Both PyModuleState and PySourceManager are singletons per module.


class QryModuleState(QryBase, QryCellT[Result[ModuleStateItem, None] | Result[None, Exception]]):
    """
    Query class that retrieves the module state for a given cell and Python module.

    This class is used to query the state of a specific cell within a Python module.

    Args:
        cell (CalcCell): The cell to query the module state for
        mod (PyModuleT): The Python module to query the state from
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT) -> None:
        """
        Initialize the query with a cell and module.

        Args:
            cell (CalcCell): The cell to query the module state for
            mod (PyModuleT): The Python module to query the state from
        """
        QryBase.__init__(self)
        self._cell = cell
        self._mod = mod

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Get the PySourceManager instance for the current module.

        Returns:
            PySourceManager: The PySourceManager instance
        """
        # avoid circular import
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
        else:
            from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
        qry = QryPySrcMgrCode(cell=self.cell, mod=self._mod)
        return self._execute_qry(qry)

    def execute(self) -> Result[ModuleStateItem, None] | Result[None, Exception]:
        """
        Execute the query to get the module state for the cell.

        Returns:
            Result: Success with ModuleStateItem if found, Failure with Exception if not found
        """
        try:
            src_mgr = self._qry_py_src_mgr()
            # if not self._cell.cell_obj in src_mgr:
            #     return Result.failure(Exception("Cell Not found ing  source manager"))

            mod_state = src_mgr.state_history
            if self._cell in mod_state:
                return Result.success(mod_state[self._cell])
            return Result.failure(Exception("No state found"))
        except Exception:
            return Result.failure(Exception("Error executing query"))

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this query.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
