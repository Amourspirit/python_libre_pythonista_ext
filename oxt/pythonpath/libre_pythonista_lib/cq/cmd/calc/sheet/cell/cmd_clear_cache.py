from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_cache_t import CmdCellCacheT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.utils.custom_ext import override


class CmdClearCache(CmdBase, CmdCellCacheT):
    """
    Command that clears specified cache keys.

    This command take no action when executed.
    The cache is clear only when this command is called by command handler.
    """

    def __init__(self, *cache_keys: str, cell: CalcCell) -> None:
        """
        Initialize the command with cache keys to clear.

        Args:
            *cache_keys: Variable number of string cache keys to clear
        """
        CmdBase.__init__(self)
        self.kind = CalcCmdKind.CELL_CACHE
        self._cache_keys = cache_keys
        self._cell = cell

    @override
    def execute(self) -> None:
        """Executes the command. Always succeeds."""
        self.success = True

    @override
    def undo(self) -> None:
        """Undoes the command. No-op since cache clearing cannot be undone."""
        return

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        """
        Gets the cache keys to clear.

        Returns:
            Tuple of cache key strings
        """
        return self._cache_keys

    @property
    def cell(self) -> CalcCell:
        return self._cell
