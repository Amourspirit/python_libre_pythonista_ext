from __future__ import annotations
from typing import Protocol
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT


class CmdHandlerCellCacheT(Protocol):
    def handle(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        ...
