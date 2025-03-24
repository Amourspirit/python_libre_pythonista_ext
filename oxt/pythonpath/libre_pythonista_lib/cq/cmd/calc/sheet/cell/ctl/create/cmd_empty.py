from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_empty import QryEmpty
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_empty import QryEmpty


class CmdEmpty(CmdSimple):
    @override
    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.EMPTY

    @override
    def _on_executing(self, ctl: Ctl) -> None:
        qry = QryEmpty(self.cell, ctl)
        self._execute_qry(qry)
