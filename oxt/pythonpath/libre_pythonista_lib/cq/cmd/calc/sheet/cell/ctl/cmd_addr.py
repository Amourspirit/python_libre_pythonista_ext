from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr as CmdPropAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr as CmdPropAddr
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.utils.result import Result


class CmdAddr(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the address of the cell such as ``sheet_index=0&cell_addr=A1``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl

        self.kind = CalcCmdKind.CELL
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = NULL_OBJ
        self._current_ctl: Dict[str, Any] | None = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_current_state(self) -> str:
        qry = QryAddr(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return ""

    @override
    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()

        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            addr = f"sheet_index={self.cell.calc_sheet.sheet_index}&cell_addr={self.cell.cell_obj}"
            if self._current_state == addr:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.addr = addr

            cmd_prop_addr = CmdPropAddr(cell=self.cell, addr=addr)
            self._execute_cmd(cmd_prop_addr)
            if cmd_prop_addr.success:
                self._success_cmds.append(cmd_prop_addr)
            else:
                raise Exception("Error setting cell address")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting address: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()

        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._ctl.addr = self._current_state

        if self._current_ctl is not None:
            self._ctl.clear()
            self._ctl.update(self._current_ctl)
            self._current_ctl = None
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
