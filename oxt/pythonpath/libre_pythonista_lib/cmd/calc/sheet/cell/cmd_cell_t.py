from __future__ import annotations
from typing import Protocol, TYPE_CHECKING


from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdCellT(CmdT, Protocol):
    @property
    def cell(self) -> CalcCell: ...
