from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING, cast

from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from ooodev.units import UnitMM100

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from com.sun.star.sheet import Shape  # service
    from com.sun.star.drawing import ControlShape  # service
    from oxt.___lo_pip___.basic_config import BasicConfig
    from ooodev.form.controls.form_ctl_base import FormCtlBase
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.shape.cmd_shape_prop import CmdShapeProp
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_default import QryColorBgDefault
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_set_location import CmdSetLocation
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.ctl_options import CtlOptions
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.kind.ctl_prop_kind import CtlPropKind
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.shape.cmd_shape_prop import CmdShapeProp
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from libre_pythonista_lib.cq.qry.calc.common.style.ctl.qry_color_bg_default import QryColorBgDefault
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.create.cmd_set_location import CmdSetLocation
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.options.ctl_options import CtlOptions

    Shape = object
    ControlShape = object


class CmdSimple(CmdBase, LogMixin, CmdCellCtlT):
    """Creates a simple control"""

    def __init__(self, cell: CalcCell, ctl: Ctl, opt: CtlOptions | None = None) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._cfg = BasicConfig()
        self.__current_ctl: Dict[str, Any] | None = None
        if opt is None:
            opt = CtlOptions()
        self._opt = opt
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        """Validates the ctl"""
        required_attributes = {"cell", "label", "ctl_code_name", "ctl_name"}

        # make a copy of the ctl dictionary because will always return True
        # when checking for an attribute directly.
        ctl_dict = self._ctl.copy_dict()

        for attrib in required_attributes:
            if not attrib in ctl_dict:
                self.log.error("Validation error. %s attribute is missing.", attrib)
                return False
        return True

    def _set_control_kind(self) -> None:
        self._ctl.control_kind = CtlKind.SIMPLE_CTL

    def _set_control_props(self) -> None:
        self._ctl.ctl_props = (
            CtlPropKind.CTL_SHAPE,
            CtlPropKind.CTL_ORIG,
            CtlPropKind.PYC_RULE,
            CtlPropKind.MODIFY_TRIGGER_EVENT,
        )

    def _set_ctl_script(self, ctl: FormCtlBase) -> None:
        """Sets the location of the control"""
        cmd_set_location = CmdSetLocation(cell=self.cell, ctl=ctl)
        self._execute_cmd(cmd_set_location)

    def _get_button_bg_color(self) -> int:
        """Gets the background color"""
        qry = QryColorBgDefault(style=self._opt.style)
        return self._execute_qry(qry)

    def _set_shape_size(self, shape: ControlShape) -> None:
        """Sets the shape size"""
        qry = QryCtlCellSizePos(cell=self.cell)
        size_pos = self._execute_qry(qry)

        height = int(size_pos.height)
        x = int(size_pos.x)
        y = int(size_pos.y)
        new_sz = Size(min(height, int(UnitMM100(455))), height)
        shape.setSize(new_sz)
        shape.setPosition(Point(x, y))

    def _set_shape_props(self, shape: Shape) -> None:
        """Sets the shape properties"""
        cmd_shape_prop = CmdShapeProp(cell=self.cell, shape=shape)
        self._execute_cmd(cmd_shape_prop)

    def _insert_control(self) -> None:
        cell_ctl = self.cell.control
        btn = cell_ctl.insert_control_button(label=self._ctl.label, name=self._ctl.ctl_name)
        shape = btn.control_shape
        self._set_shape_size(shape)
        btn.printable = False
        btn.model.BackgroundColor = self._get_button_bg_color()  # type: ignore
        btn.tab_stop = False
        self._set_ctl_script(btn)
        self._set_shape_props(cast(Shape, shape))

    def _on_executing(self, ctl: Ctl) -> None:
        pass

    @override
    def execute(self) -> None:
        self.success = False
        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return
        self._state_changed = False
        try:
            if self.__current_ctl is None:
                self.__current_ctl = self._ctl.copy_dict()
            self._insert_control()
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
            self.cell.control.current_control = None
            if self.__current_ctl is not None:
                self._ctl.clear()
                self._ctl.update(self.__current_ctl)
                self.__current_ctl = None
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
