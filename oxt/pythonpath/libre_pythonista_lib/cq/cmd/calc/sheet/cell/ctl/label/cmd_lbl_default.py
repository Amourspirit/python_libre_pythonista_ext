from __future__ import annotations
from typing import List, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.label.qry_lbl_default import QryLblDefault


class CmdLblDefault(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the default label of the cell such as ``<>``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl

        self.kind = CalcCmdKind.CELL
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = None

    def _qry_label(self) -> str:
        qry = QryLblDefault(cell=self.cell)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        try:
            value = self._qry_label()
            self._current_state = self._ctl.get("label")
            if self._current_state == value:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.label = value
            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting address: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        if self._current_state is None:
            if "label" in self._ctl:
                del self._ctl["label"]
            return
        self._ctl.label = self._current_state
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
