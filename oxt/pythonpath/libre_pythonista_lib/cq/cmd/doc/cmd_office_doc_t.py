from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT


class CmdOfficeDocT(CmdT, Protocol):
    def __init__(self, doc: OfficeDocumentT, *args: object, **kwargs: object) -> None: ...
