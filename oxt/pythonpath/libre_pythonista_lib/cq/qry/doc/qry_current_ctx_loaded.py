from __future__ import annotations


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CTX_LOADED
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.doc.qry_doc_globals import QryDocGlobals
    from libre_pythonista_lib.const.cache_const import DOC_CTX_LOADED
    from libre_pythonista_lib.utils.result import Result


class QryCurrentCtxLoaded(QryBase, QryT[bool]):
    """Query to check if the current document context is loaded."""

    def __init__(self, uid: str | None = None) -> None:
        """
        Initialize the query.

        Args:
            uid (str | None, optional): The runtime unique id of the document. Defaults to None.
        """
        QryBase.__init__(self)
        self._uid = uid

    def _qry_globals(self) -> Result[DocGlobals, None] | Result[None, Exception]:
        """
        Get the document globals using QryDocGlobals.

        Returns:
            Result: Success with DocGlobals or Failure with None/Exception
        """
        qry = QryDocGlobals(uid=self._uid)
        return self._execute_qry(qry)

    def execute(self) -> bool:
        """
        Executes the query to check if the current context is loaded.

        Returns:
            bool: True if the current context is loaded (DOC_CTX_LOADED == "1"), False otherwise.
        """
        doc_globals = self._qry_globals()
        if Result.is_failure(doc_globals):
            return False
        if DOC_CTX_LOADED not in doc_globals.data.mem_cache:
            return False
        key_val = doc_globals.data.mem_cache[DOC_CTX_LOADED]
        return key_val == "1"
