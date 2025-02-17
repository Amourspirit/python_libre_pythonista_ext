from __future__ import annotations
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache_t import CmdHandlerCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_handler_cell_cache_t import CmdHandlerCellCacheT
    from libre_pythonista_lib.query.qry_handler import QryHandler
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_cache import QryCellCache


class CmdHandlerCellCache(CmdHandlerCellCacheT):
    def handle(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCellCache(cmd.cell)
        cache = cast("MemCache", QryHandler().handle(cache_qry))
        if not cache:
            return

        for key in cmd.cache_keys:
            if key in cache:
                del cache[key]
        cmd.execute()
