from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_error import QryColorBgError
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_error import QryError
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_simple import CmdSimple
    from libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_error import QryColorBgError
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_error import QryError
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override


class CmdError(CmdSimple):
    @override
    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.ERROR

    @override
    def _on_executing(self, ctl: Ctl) -> None:
        qry = QryError(self.cell, ctl)
        self._execute_qry(qry)

    @override
    def _get_button_bg_color(self) -> int:
        """Gets the background color"""
        qry = QryColorBgError()
        return self._execute_qry(qry)
