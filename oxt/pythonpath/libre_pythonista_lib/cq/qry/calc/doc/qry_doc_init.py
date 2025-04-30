from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.utils.result import Result

    DocGlobals = Any

# see: libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_init.CmdDocInit


class QryDocInit(QryBase, QryT[bool]):
    def __init__(self, doc: CalcDoc | None = None) -> None:
        """Constructor

        Args:
            doc (CalcDoc, optional): The Calc document. Defaults to None.
        """
        QryBase.__init__(self)
        self._doc = doc

    def _get_globals(self) -> DocGlobals | None:
        uid = self._doc.runtime_uid if self._doc else None
        qry = QryDocGlobals(uid=uid)
        qry_result = self._execute_qry(qry)
        if Result.is_success(qry_result):
            return qry_result.data
        return None

    def execute(self) -> bool:
        """
        Executes the query to check if the document is initialized.

        Returns:
            bool: True if the document is initialized, False otherwise.
        """
        doc_globals = self._get_globals()
        if doc_globals is None:
            return False
        if DOC_INIT_COMPLETED not in doc_globals.mem_cache:
            return False
        key_val = doc_globals.mem_cache[DOC_INIT_COMPLETED]
        return key_val == "1"
