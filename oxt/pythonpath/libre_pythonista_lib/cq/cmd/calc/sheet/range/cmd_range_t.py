from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


from ooodev.calc import CalcCellRange

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT


class CmdRangeT(CmdT, Protocol):
    @property
    def cell_range(self) -> CalcCellRange: ...
