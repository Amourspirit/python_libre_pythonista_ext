from __future__ import annotations
from typing import Tuple, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT


class CmdCacheT(CmdT, Protocol):
    @property
    def cache_keys(self) -> Tuple[str, ...]: ...
