from __future__ import annotations
from typing import List, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_rr_value import QryRRValue
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault
else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.label.cmd_lbl_default import CmdLblDefault
    from libre_pythonista_lib.cq.qry.general.qry_rr_value import QryRRValue
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault


class CmdLblRR(CmdLblDefault):
    """Sets the  label of the cell from the resource resolver"""

    def __init__(self, cell: CalcCell, ctl: Ctl, res_key: str) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the label for.
            ctl (Ctl): Control to set the label for.
            res_key (str): Resource key to get the label from.
        """
        super().__init__(cell, ctl)
        self._res_key = res_key

    def _qry_lbl_default(self) -> str:
        qry = QryLblDefault(cell=self.cell, ctl=self._ctl)
        return self._execute_qry(qry)

    @override
    def _qry_label(self) -> str:
        qry = QryRRValue(res_key=self._res_key)
        result = self._execute_qry(qry)
        default = self._qry_lbl_default()
        return f"{default} {result}"
