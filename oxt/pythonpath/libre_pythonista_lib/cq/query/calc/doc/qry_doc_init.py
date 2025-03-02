from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_doc_globals import QryDocGlobals
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.qry_t import QryT
    from libre_pythonista_lib.const.cache_const import DOC_INIT_COMPLETED
    from libre_pythonista_lib.cq.query.doc.qry_doc_globals import QryDocGlobals

    DocGlobals = Any

# see: libre_pythonista_lib.cq.cmd.calc.doc.cmd_doc_init.CmdDocInit


class QryDocInit(QryBase, QryT[bool]):
    def __init__(self) -> None:
        QryBase.__init__(self)

    def _get_globals(self) -> DocGlobals | None:
        qry = QryDocGlobals()
        return self._execute_qry(qry)

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
