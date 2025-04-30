from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.utils.result import Result


class QryDocGlobals(QryBase, QryT[Result[DocGlobals, None] | Result[None, Exception]]):
    def __init__(self, uid: str | None = None) -> None:
        """Constructor

        Args:
            uid (str, optional): The RuntimeUID of the document. Defaults to None.
        """
        QryBase.__init__(self)
        self._uid = uid

    def execute(self) -> Result[DocGlobals, None] | Result[None, Exception]:
        """
        Executes the query to get the document globals.

        Returns:
            Result: Success with DocGlobals or Failure with Exception
        """
        try:
            doc_globals = DocGlobals.get_current(uid=self._uid)
            return Result.success(doc_globals)
        except ValueError as e:
            return Result.failure(e)
