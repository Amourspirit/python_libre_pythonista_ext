from __future__ import annotations
from typing import Any, Dict, cast, List, TYPE_CHECKING, Union

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker


class CmdCtlShapeNameImg(CmdBase, LogMixin, CmdCellCtlT):
    """Sets Control Shape name such as ``SHAPE_libre_pythonista_cell_id_1tyVH7L4Vl4Azd``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._is_deleted = None
        self._keys = cast("KeyMaker", NULL_OBJ)
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = self._ctl.ctl_shape_name
        self._current_ctl: Union[Dict[str, Any], None] = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        """Validates the ctl"""
        required_attributes = {"ctl_name", "ctl_code_name"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()

        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.error("Validation error. %s attribute is missing.", attrib)
                return False
        return True

    def _get_keys(self) -> KeyMaker:
        qry = QryKeyMaker()
        return self._execute_qry(qry)

    def _qry_shape_img_name(self) -> str:
        """
        Generates a unique shape name for the image based on the cell's code name.

        Args:
            code_name: The cell's code name

        Returns:
            str: Generated shape name for the image
        """
        qry = QryShapeNameImg(code_name=self._ctl.ctl_code_name)
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False

        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return

        if self._keys is NULL_OBJ:
            self._keys = self._get_keys()
        self._success_cmds.clear()
        if not self._ctl.ctl_name:
            self.log.error("Error setting cell address: ctl_name is empty")
            return
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            control_shape_name = self._qry_shape_img_name()

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

        try:
            if self._current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self._current_ctl)
                self._current_ctl = None

        except Exception:
            self.log.exception("Error executing undo command")
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
