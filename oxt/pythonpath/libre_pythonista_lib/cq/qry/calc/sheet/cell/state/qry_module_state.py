from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_state import PyModuleState
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.code.py_module_state import PyModuleState
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT


class QryModuleState(QryBase, QryCellT[ModuleStateItem | None]):
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

    def execute(self) -> ModuleStateItem | None:
        """
        Execute the query to get the module state for the cell.

        Returns:
            ModuleStateItem | None: The module state item if found, None otherwise
        """
        mod_state = PyModuleState(self._mod)
        if self._cell in mod_state:
            return mod_state[self._cell]
        return None

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this query.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
