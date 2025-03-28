from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.draw_page.cmd_add_image_linked import (
        CmdAddImageLinked,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.cmd.cmd_t import CmdT
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.draw_page.cmd_add_image_linked import CmdAddImageLinked
    from libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg


class CmdMatPlotFigureImg(CmdBase, LogMixin, CmdCellCtlT):
    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._ctl = ctl
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_shape_name = self._ctl.ctl_shape_name
        self._success_cmds: List[CmdT] = []
        self._current_ctl: Dict[str, Any] | None = None

    def _validate(self) -> bool:
        """Validates the ctl"""
        required_attributes = {"cell", "ctl_code_name", "ctl_storage_location"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()

        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.error("Validation error. %s attribute is missing.", attrib)
                return False
        return True

    def _cmd_add_image_linked(self) -> bool:
        """
        Sets a unique code name for the cell.

        Returns:
            bool: True if code name was successfully set, False otherwise
        """
        cmd = CmdAddImageLinked(cell=self.cell, fnm=self._ctl.ctl_storage_location)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
            return True
        return False

    def _qry_shape_img_name(self, code_name: str) -> str:
        """
        Generates a unique shape name for the image based on the cell's code name.

        Args:
            code_name: The cell's code name

        Returns:
            str: Generated shape name for the image
        """
        qry = QryShapeNameImg(code_name=code_name)
        return self._execute_qry(qry)

    def _on_executing(self, ctl: Ctl) -> None:
        pass

    @override
    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return
        try:
            if self._current_ctl is None:
                self._current_ctl = self._ctl.copy_dict()
            if not self._cmd_add_image_linked():
                raise Exception("Error adding image linked")
            self._ctl.ctl_shape_name = "SHAPE_" + self._qry_shape_img_name(self._ctl.ctl_code_name)

            cmd_shape = CmdShape(cell=self.cell, name=self._ctl.ctl_shape_name)
            self._execute_cmd(cmd_shape)
            if cmd_shape.success:
                self._success_cmds.append(cmd_shape)
            else:
                raise Exception("Error setting cell shape name")

            self._on_executing(self._ctl)
            self._state_changed = True
        except Exception as e:
            self.log.exception("Error inserting control: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        for cmd in self._success_cmds:
            self._execute_cmd_undo(cmd)
        self._success_cmds.clear()

        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
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
