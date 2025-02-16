from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache_t import CmdHandlerSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
else:
    from libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache_t import CmdHandlerSheetCacheT
    from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache


class CmdHandlerSheetCache(CmdHandlerSheetCacheT):
    def handle(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache = get_sheet_cache(cmd.sheet)
        if cmd.cache_key in cache:
            del cache[cmd.cache_key]
        cmd.execute()
