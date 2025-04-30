from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT, TResult
else:
    from libre_pythonista_lib.cq.qry.qry_t import QryT, TResult


class QryOfficeDocT(QryT[TResult], Protocol):
    def __init__(self, doc: OfficeDocumentT, *args: object, **kwargs: object) -> None: ...
