from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
else:
    from libre_pythonista_lib.cmd.cmd_t import CmdT


class CmdSheetT(CmdT, Protocol):
    @property
    def sheet(self) -> CalcSheet: ...
