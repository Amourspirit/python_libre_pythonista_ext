from __future__ import annotations
from typing import cast, List, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker


class CmdCtlShapeName(CmdBase, LogMixin, CmdCellCtlT):
    """Sets Control Shape name such as ``SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._is_deleted = None
        self._config = BasicConfig()
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = self._ctl.ctl_shape_name

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()

        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        if not self._ctl.ctl_code_name:
            self.log.error("Error setting cell address: ctl_code_name is empty")
            return
        try:
            control_shape_name = f"SHAPE_{self._config.general_code_name}_ctl_cell_{self._ctl.ctl_code_name}"

            if self._current_state and control_shape_name == self._current_state:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.ctl_shape_name = control_shape_name

            cmd_shape = CmdShape(cell=self.cell, name=self._ctl.ctl_shape_name)
            self._execute_cmd(cmd_shape)
            if cmd_shape.success:
                self._success_cmds.append(cmd_shape)
            else:
                raise Exception("Error setting cell shape name")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting control shape name: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()
        self._ctl.ctl_shape_name = self._current_state
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
