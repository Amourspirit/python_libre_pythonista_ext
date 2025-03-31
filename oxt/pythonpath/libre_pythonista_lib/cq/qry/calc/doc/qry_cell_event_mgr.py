from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_event_mgr import CellEventMgr
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.cell_event_mgr import CellEventMgr
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryCellEventMgr(QryBase, LogMixin, QryDocT[CellEventMgr]):
    """Gets the singleton CellEventMgr"""

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

    def _qry_py_src_mgr(self) -> PySourceManager:
        """Gets the PySourceManager via query"""
        qry = QryPySrcMgr(doc=self._doc, mod=self._mod)
        return self._execute_qry(qry)

    def execute(self) -> CellEventMgr:
        """Executes the query to get the singleton CellEventMgr"""
        src_mgr = self._qry_py_src_mgr()
        return CellEventMgr(src_mgr=src_mgr)
