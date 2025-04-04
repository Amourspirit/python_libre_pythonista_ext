from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.ctl_options import CtlOptions
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_mat_plot_figure import (
        QryMatPlotFigure,
    )
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.ctl_options import CtlOptions
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_mat_plot_figure import QryMatPlotFigure


class CmdMatPlotFigure(CmdBase, LogMixin, CmdCellCtlT):
    def __init__(self, cell: CalcCell, ctl: Ctl, opt: CtlOptions | None = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._ctl = ctl
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_ctl: Dict[str, Any] | None = None
        if opt is None:
            opt = CtlOptions()
        self._opt = opt
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        """Validates the ctl"""
        required_attributes = {"cell", "ctl_code_name"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()

        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.error("Validation error. %s attribute is missing.", attrib)
                return False
        return True

    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.MAT_PLT_FIGURE

    def _set_control_props(self) -> None:
        self._ctl.ctl_props = (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )

    def _on_executing(self, ctl: Ctl) -> None:
        qry = QryMatPlotFigure(self.cell, ctl)
        self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False
        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return
        self._state_changed = False
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            self._on_executing(self._ctl)
            self._set_control_kind()
            self._set_control_props()
            self._state_changed = True
        except Exception:
            self.log.exception("Error inserting control")
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        try:
            if self._current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self._current_ctl)
                self._current_ctl = None
        except Exception:
            self.log.exception("Error undoing control")
            return
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell
