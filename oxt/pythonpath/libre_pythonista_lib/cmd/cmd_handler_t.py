from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdHandlerT(Protocol):
    def handle(self, cmd: CmdT) -> None:  # noqa: ANN401
        ...
