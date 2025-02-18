from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdDocT(CmdT, Protocol):
    def __init__(self, doc: CalcDoc) -> None: ...
