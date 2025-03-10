from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple


class CmdStr(CmdSimple):
    pass
