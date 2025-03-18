from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_state import PyModuleState
    from oxt.pythonpath.libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.code.py_module_state import PyModuleState
    from libre_pythonista_lib.code.module_state_item import ModuleStateItem
    from libre_pythonista_lib.cq.qry.qry_t import QryT


# tested in: tests/test_cmd_qry/test_cell/state/test_qry_module_state_last_item.py


class QryModuleStateLastItem(QryBase, QryT[ModuleStateItem | None]):
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

    def execute(self) -> ModuleStateItem | None:
        """
        Execute the query to get the last state item.

        Returns:
            ModuleStateItem | None: The last state item if it exists, None otherwise
        """
        mod_state = PyModuleState(self._mod)
        return mod_state.get_last_item()
