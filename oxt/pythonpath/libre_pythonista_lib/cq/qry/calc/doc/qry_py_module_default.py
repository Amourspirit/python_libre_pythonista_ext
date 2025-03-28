from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.code.py_module import PyModule

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.code.py_module import PyModule


class QryPyModuleDefault(QryBase, QryT[PyModule]):
    """Gets the singleton PyModule"""

    def __init__(self) -> None:
        """Constructor"""
        QryBase.__init__(self)

    def execute(self) -> PyModule:
        """Executes the query to get the singleton PyModule"""
        return PyModule()
