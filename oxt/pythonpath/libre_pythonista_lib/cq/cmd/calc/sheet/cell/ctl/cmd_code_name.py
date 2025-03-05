from __future__ import annotations
from typing import List, TYPE_CHECKING

from ooodev.utils import gen_util

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import (
        CmdCodeName as CmdPropCodeName,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName as CmdPropCodeName
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.extra.cmd_cell_extra_set import CmdCellExtraSet
    from ___lo_pip___.basic_config import BasicConfig


class CmdCodeName(CmdBase, LogMixin, CmdCellCtlT):
    """Sets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._cmd_handler = CmdHandler()
        self._success_commands: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._current_code_name = self._ctl.ctl_code_name
        self._current_dict_code_name = self.cell.extra_data.get("code_name", "")

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        self._success_commands.clear()
        try:
            code_name = "id_" + gen_util.Util.generate_random_alpha_numeric(14)
            cmd_prop_code_name = CmdPropCodeName(cell=self.cell, name=code_name)
            self._cmd_handler.handle(cmd_prop_code_name)

            if cmd_prop_code_name.success:
                self._success_commands.append(cmd_prop_code_name)
            else:
                self.log.error("Error setting cell code name")
                return

            cmd_cell_extra_set = CmdCellExtraSet(cell=self.cell, name="code_name", value=code_name)
            self._cmd_handler.handle(cmd_cell_extra_set)
            if cmd_cell_extra_set.success:
                self._success_commands.append(cmd_cell_extra_set)
            else:
                self.log.error("Error setting cell extra data")
                self._undo()
                return

            if self._current_code_name == code_name:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.ctl_code_name = code_name
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting code name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        for cmd in self._success_commands:
            cmd.undo()
        self._success_commands.clear()
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._ctl.ctl_code_name = self._current_code_name
        self.cell.extra_data.code_name = self._current_dict_code_name
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
