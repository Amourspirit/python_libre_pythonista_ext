from __future__ import annotations
from typing import Tuple, Protocol, TYPE_CHECKING


from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT


class CmdCellCacheT(CmdCellT, Protocol):
    @property
    def cache_keys(self) -> Tuple[str, ...]: ...
