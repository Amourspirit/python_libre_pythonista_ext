# region Imports
from __future__ import annotations
from typing import Any, Iterable, cast, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.utils.cache import MemCache
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_cache import QryCache
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache import QryCellCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache import QrySheetCache
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_cache_t import CmdSheetCacheT
    from libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.cq.qry.general.qry_cache import QryCache
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_cache import QryCellCache
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_cache import QrySheetCache
    from libre_pythonista_lib.cq.qry.qry_handler import QryHandler

    MemCache = Any

# endregion Imports


class CmdHandler(CmdHandlerT):
    # region Handle methods
    def __init__(self) -> None:
        self._undo_stack: List[CmdT] = []
        self._redo_stack: List[CmdT] = []

    def handle(self, cmd: CmdT) -> None:  # noqa: ANN401
        if cmd.kind in (CalcCmdKind.SIMPLE, CalcCmdKind.SHEET, CalcCmdKind.CELL):
            self._handle_simple(cmd)
        elif cmd.kind == CalcCmdKind.SIMPLE_CACHE:
            self._handle_simple_cache(cast(CmdCacheT, cmd))
        elif cmd.kind == CalcCmdKind.CELL_CACHE:
            self._handle_cell_cache(cast(CmdCellCacheT, cmd))
        elif cmd.kind == CalcCmdKind.SHEET_CACHE:
            self._handle_sheet_cache(cast(CmdSheetCacheT, cmd))
        else:
            raise NotImplementedError

    def _handle_simple(self, cmd: CmdT) -> None:
        cmd.execute()
        if cmd.success:
            self._undo_stack.append(cmd)
            self._redo_stack.clear()

    def _handle_simple_cache(self, cmd: CmdCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCache()
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.execute()
        if cmd.success:
            self._undo_stack.append(cmd)
            self._redo_stack.clear()

        # Executing some commands may call a query which will add the key back into the cache.
        # So we need to remove it again after the command is executed to reflect new values that the command executed.
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_cell_cache(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCellCache(cmd.cell)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.execute()
        if cmd.success:
            self._undo_stack.append(cmd)
            self._redo_stack.clear()

        # Executing some commands may call a query which will add the key back into the cache.
        # So we need to remove it again after the command is executed to reflect new values that the command executed.
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_sheet_cache(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache_qry = QrySheetCache(cmd.sheet)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return
        self._clear_cache(cache, cmd.cache_keys)
        cmd.execute()
        if cmd.success:
            self._undo_stack.append(cmd)
            self._redo_stack.clear()

        # Executing some commands may call a query which will add the key back into the cache.
        # So we need to remove it again after the command is executed to reflect new values that the command executed.
        self._clear_cache(cache, cmd.cache_keys)

    # endregion Handle methods

    # region Undo methods

    def handle_undo(self, cmd: CmdT) -> None:  # noqa: ANN401
        if cmd.kind in (CalcCmdKind.SIMPLE, CalcCmdKind.SHEET, CalcCmdKind.CELL):
            self._handle_undo_simple(cmd)
        elif cmd.kind == CalcCmdKind.SIMPLE_CACHE:
            self._handle_undo_simple_cache(cast(CmdCacheT, cmd))
        elif cmd.kind == CalcCmdKind.CELL_CACHE:
            self._handle_undo_cell_cache(cast(CmdCellCacheT, cmd))

    def _handle_undo_simple(self, cmd: CmdT) -> None:
        cmd.undo()

    def _handle_undo_simple_cache(self, cmd: CmdCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCache()
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.undo()
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_undo_cell_cache(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCellCache(cmd.cell)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.undo()
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_undo_sheet_cache(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache_qry = QrySheetCache(cmd.sheet)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.undo()
        self._clear_cache(cache, cmd.cache_keys)

    # endregion Undo methods

    # region Redo methods

    def handle_redo(self, cmd: CmdT) -> None:  # noqa: ANN401
        if cmd.kind in (CalcCmdKind.SIMPLE, CalcCmdKind.SHEET, CalcCmdKind.CELL):
            self._handle_redo_simple(cmd)
        elif cmd.kind == CalcCmdKind.SIMPLE_CACHE:
            self._handle_redo_simple_cache(cast(CmdCacheT, cmd))
        elif cmd.kind == CalcCmdKind.CELL_CACHE:
            self._handle_redo_cell_cache(cast(CmdCellCacheT, cmd))
        elif cmd.kind == CalcCmdKind.SHEET_CACHE:
            self._handle_redo_sheet_cache(cast(CmdSheetCacheT, cmd))
        else:
            raise NotImplementedError
        return

    def _handle_redo_simple(self, cmd: CmdT) -> None:
        cmd.redo()

    def _handle_redo_simple_cache(self, cmd: CmdCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCache()
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.redo()
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_redo_cell_cache(self, cmd: CmdCellCacheT) -> None:  # noqa: ANN401
        cache_qry = QryCellCache(cmd.cell)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.redo()
        self._clear_cache(cache, cmd.cache_keys)

    def _handle_redo_sheet_cache(self, cmd: CmdSheetCacheT) -> None:  # noqa: ANN401
        cache_qry = QrySheetCache(cmd.sheet)
        cache = cast(MemCache, QryHandler().handle(cache_qry))
        if not cache:
            return

        self._clear_cache(cache, cmd.cache_keys)
        cmd.redo()
        self._clear_cache(cache, cmd.cache_keys)

    # endregion Redo methods

    # region Cache methods
    def _clear_cache(self, cache: MemCache, keys: Iterable[str]) -> None:
        for key in keys:
            if key in cache:
                del cache[key]

    # endregion Cache methods

    # region Undo/Redo stack methods

    def undo(self) -> None:
        """Undo the last command"""
        if self._undo_stack:
            cmd = self._undo_stack.pop()
            self.handle_undo(cmd)
            self._redo_stack.append(cmd)

    def redo(self) -> None:
        """Redo the last command"""
        if self._redo_stack:
            cmd = self._redo_stack.pop()
            self.handle_redo(cmd)
            self._undo_stack.append(cmd)

    # endregion Undo/Redo stack methods
