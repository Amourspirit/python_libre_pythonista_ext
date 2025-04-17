from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.doc.cmd_py_module_default import CmdPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module import PyModule
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.cq.cmd.calc.doc.cmd_py_module_default import CmdPyModuleDefault
    from libre_pythonista_lib.utils.result import Result

    PyModuleT = Any


class QryPyModuleDefault(QryBase, QryT[PyModuleT]):
    """Query that retrieves the default Python module from document globals cache."""

    def __init__(self) -> None:
        """Constructor."""
        QryBase.__init__(self)

    def _get_globals(self) -> DocGlobals | None:
        """
        Gets the document globals using QryDocGlobals.

        Returns:
            DocGlobals | None: Document globals if successful, None otherwise
        """
        qry = QryDocGlobals()
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return None

    def execute(self) -> PyModuleT:
        """
        Executes the query to get the default Python module.

        Returns:
            PyModuleT: The cached default Python module if it exists, otherwise a new PyModule instance
        """
        doc_globals = self._get_globals()
        if doc_globals is None:
            return PyModule()

        if CmdPyModuleDefault.CACHE_KEY in doc_globals.mem_cache:
            return doc_globals.mem_cache[CmdPyModuleDefault.CACHE_KEY]
        return PyModule()
