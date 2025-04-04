from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryPySrcMgr(QryBase, LogMixin, QryDocT[PySourceManager]):
    """Gets the singleton PySourceManager"""

    def __init__(self, doc: CalcDoc, mod: PyModuleT | None = None) -> None:
        """Constructor

        Args:
            doc (CalcDoc): The Calc document
            mod (PyModuleT, optional): The Python module. Defaults to None.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._mod = mod
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _qry_mod(self) -> PyModuleT:
        """Gets the Python module"""
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def execute(self) -> PySourceManager:
        """Executes the query to get the singleton PySourceManager"""
        if self._mod is None:
            self._mod = self._qry_mod()
        return PySourceManager(doc=self._doc, mod=self._mod)
