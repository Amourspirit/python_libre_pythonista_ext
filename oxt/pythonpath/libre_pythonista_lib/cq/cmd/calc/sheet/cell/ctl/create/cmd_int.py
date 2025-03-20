from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override


class CmdInt(CmdSimple):
    @override
    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.INTEGER
