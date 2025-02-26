from __future__ import annotations
from typing import Iterable, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import MemCache
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_handler import QryHandler
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.query.calc.sheet.cell.qry_cell_cache import QryCellCache
    from libre_pythonista_lib.cq.query.calc.sheet.qry_sheet_cache import QrySheetCache
    from libre_pythonista_lib.cq.query.qry_handler import QryHandler


class CmdHandler(CmdHandlerT):
    def handle(self, cmd: CmdT) -> None:  # noqa: ANN401
        if cmd.kind in (CalcCmdKind.SIMPLE, CalcCmdKind.SHEET, CalcCmdKind.CELL):
            self._handle_simple(cmd)
        elif cmd.kind == CalcCmdKind.CELL_CACHE:
            self._handle_cell_cache(cast(CmdCellCacheT, cmd))
        elif cmd.kind == CalcCmdKind.SHEET_CACHE:
            self._handle_sheet_cache(cast(CmdSheetCacheT, cmd))
        else:
            raise NotImplementedError

    def _handle_simple(self, cmd: CmdT) -> None:
        cmd.execute()

    def _handle_cell_cache(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCellCache(cmd.cell)
        cache = cast("MemCache", QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)

        cmd.execute()

        # Executing some commands may call a query which will add the key back into the cache.
        # So we need to remove it again after the command is executed to reflect new values that the command executed.
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_sheet_cache(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache_qry = QrySheetCache(cmd.sheet)
        cache = cast("MemCache", QryHandler().handle(cache_qry))
        if not cache:
            return
        self._clear_cache(cache, cmd.cache_keys)
        cmd.execute()

        # Executing some commands may call a query which will add the key back into the cache.
        # So we need to remove it again after the command is executed to reflect new values that the command executed.
        self._clear_cache(cache, cmd.cache_keys)

    def _clear_cache(self, cache: MemCache, keys: Iterable[str]) -> None:
        for key in keys:
            if key in cache:
                del cache[key]
