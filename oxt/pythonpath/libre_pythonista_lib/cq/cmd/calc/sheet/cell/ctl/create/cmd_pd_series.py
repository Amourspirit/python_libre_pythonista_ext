from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_pd_df import CmdPdDf
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_series import QryPdSeries
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_pd_df import CmdPdDf
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_series import QryPdSeries


class CmdPdSeries(CmdPdDf):
    @override
    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.SERIES

    @override
    def _on_executing(self, ctl: Ctl) -> None:
        qry = QryPdSeries(self.cell, ctl)
        self._execute_qry(qry)
