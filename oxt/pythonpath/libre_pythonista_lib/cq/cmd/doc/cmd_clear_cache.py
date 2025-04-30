from __future__ import annotations
from typing import cast, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.utils.custom_ext import override


class CmdClearCache(CmdBase, CmdCacheT):
    """
    Command that clears specified cache keys.

    This command take no action when executed.
    The cache is clear only when this command is called by command handler.
    """

    def __init__(self, *cache_keys: str) -> None:
        """
        Initialize the command with cache keys to clear.

        Args:
            *cache_keys: Variable number of string cache keys to clear
        """
        CmdBase.__init__(self)
        self.kind = CalcCmdKind.SIMPLE_CACHE
        self._cache_keys = cache_keys

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
