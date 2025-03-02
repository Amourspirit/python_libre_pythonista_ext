from __future__ import annotations

from typing import TYPE_CHECKING
import contextlib


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.qry_t import QryT
    from libre_pythonista_lib.doc.doc_globals import DocGlobals


class QryDocGlobals(QryBase, QryT[DocGlobals | None]):
    def __init__(self) -> None:
        QryBase.__init__(self)

    def execute(self) -> DocGlobals | None:
        """
        Executes the query to get the document globals.

        Returns:
            DocGlobals: The document globals if successful, otherwise None.
        """
        with contextlib.suppress(ValueError):
            return DocGlobals.get_current()
        return None
