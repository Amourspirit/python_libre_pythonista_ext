from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING


from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT

    Ctl = Any


class CmdCellCtlT(CmdCellT, Protocol):
    def __init__(self, cell: CalcCell, ctl: Ctl) -> None: ...
