from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_simple import QrySimple
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_simple import QrySimple
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override


class QryStr(QrySimple):
    """Sets Control String properties"""

    @override
    def _set_control_kind(self) -> None:
        if self._ctl is None:
            self.log.debug("_set_control_kind() No control found. Returning.")
            return
        self._ctl.control_kind = CtlKind.STRING
