from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state import PyModuleState
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state import PyModuleState
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.utils.result import Result


# tested in: tests/test_cmd_qry/test_cell/state/test_qry_module_state_last_item.py


class QryModuleStateLastItem(QryBase, QryT[Result[ModuleStateItem, None] | Result[None, Exception]]):
    """
    Query to get the last state item of a Python module.

    Inherits from QryBase and QryCellT with a return type of ModuleStateItem or None.
    """

    def __init__(self, mod: PyModuleT) -> None:
        """
        Initialize the query.

        Args:
            mod: The Python module to query the state from
        """
        QryBase.__init__(self)
        self._mod = mod

    def execute(self) -> Result[ModuleStateItem, None] | Result[None, Exception]:
        """
        Execute the query to get the last state item.

        Returns:
            Result: Success with ModuleStateItem if found, Failure with Exception if not found
        """
        mod_state = PyModuleState(self._mod)
        result = mod_state.get_last_item()
        if result is None:
            return Result.failure(Exception("No state found"))
        return Result.success(result)
