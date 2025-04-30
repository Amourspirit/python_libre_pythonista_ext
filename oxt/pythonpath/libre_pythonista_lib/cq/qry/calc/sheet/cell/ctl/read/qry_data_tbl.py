from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_df import QryPdDf
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_pd_df import QryPdDf
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.custom_ext import override


class QryDataTbl(QryPdDf):
    """Sets Control Data Table properties"""

    @override
    def _set_control_kind(self) -> None:
        if self._ctl is None:
            self.log.debug("_set_control_kind() No control found. Returning.")
            return
        self._ctl.control_kind = CtlKind.DATA_TABLE
