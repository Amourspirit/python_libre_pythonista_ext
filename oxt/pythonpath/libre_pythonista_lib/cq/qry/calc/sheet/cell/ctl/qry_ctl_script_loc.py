from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_script_name import QryCtlScriptName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_script_name import QryCtlScriptName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista.basic_config import BasicConfig


class QryCtlScriptLoc(QryBase, LogMixin, QryCellT[str]):
    """
    Gets the script location of the cell such as ``oxt_name.oxt|python|scripts|py_script_sheet_ctl_click$macro_lp_sheet_ctl_click``

    Assigns the script location to the ``ctl`` as property ``ctl_script_loc``.
    """

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl
        self._cfg = BasicConfig()

    def _get_script_name(self) -> str:
        qry = QryCtlScriptName(cell=self.cell, ctl=self._ctl)
        return self._execute_qry(qry)

    def execute(self) -> str:
        """
        Executes the query to get the script location.

        Returns:
            str: The script Location if successful.
        """

        script_name = self._get_script_name()
        script_loc = f"{script_name}${self._cfg.macro_lp_sheet_ctl_click}"
        if self._ctl is not None:
            self._ctl.ctl_script_loc = script_loc
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return script_loc

    @property
    def cell(self) -> CalcCell:
        return self._cell
