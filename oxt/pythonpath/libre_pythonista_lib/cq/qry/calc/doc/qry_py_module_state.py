from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_state import PyModuleState
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.code.py_module_state import PyModuleState
    from libre_pythonista_lib.log.log_mixin import LogMixin

    PyModuleT = Any


class QryPyModuleState(QryBase, LogMixin, QryT[PyModuleState]):
    """Gets the singleton PyModuleState"""

    def __init__(self, mod: PyModuleT | None = None) -> None:
        """Constructor

        Args:
            mod (PyModuleT, optional): The Python module. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._mod = mod
        self.log.debug("init done")

    def _qry_mod(self) -> PyModuleT:
        """Gets the Python module"""
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def execute(self) -> PyModuleState:
        """Executes the query to get the singleton PyModuleState"""
        if self._mod is None:
            self._mod = self._qry_mod()
        return PyModuleState(mod=self._mod)
