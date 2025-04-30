from __future__ import annotations
from typing import Tuple, Protocol, TYPE_CHECKING

from ooodev.calc import CalcSheet

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT


class CmdSheetCacheT(CmdSheetT, Protocol):
    @property
    def cache_keys(self) -> Tuple[str, ...]: ...
