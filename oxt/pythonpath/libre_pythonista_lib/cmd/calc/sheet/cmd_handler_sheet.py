from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cmd.cmd_handler_t import CmdHandlerT
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdHandlerSheet(CmdHandlerT):
    def handle(self, cmd: CmdT) -> Any:  # noqa: ANN401
        return cmd.execute()
