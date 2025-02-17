from __future__ import annotations
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache_t import CmdHandlerSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
else:
    from libre_pythonista_lib.cmd.calc.sheet.cmd_handler_sheet_cache_t import CmdHandlerSheetCacheT
    from libre_pythonista_lib.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache import QrySheetCache


class CmdHandlerSheetCache(CmdHandlerSheetCacheT):
    def handle(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache_qry = QrySheetCache(cmd.sheet)
        cache = cast("MemCache", QryHandler().handle(cache_qry))
        if not cache:
            return
        for key in cmd.cache_keys:
            if key in cache:
                del cache[key]
        cmd.execute()
