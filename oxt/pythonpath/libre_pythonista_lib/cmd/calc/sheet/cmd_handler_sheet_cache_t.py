from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
else:
    from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT


class CmdHandlerSheetCacheT(Protocol):
    def handle(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        ...
