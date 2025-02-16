from __future__ import annotations
import contextlib
from typing import cast, Tuple, TYPE_CHECKING

from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from com.sun.star.awt import XActionListener

from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.utils.color import StandardColor
from ooodev.units import UnitMM100
from ooodev.utils.kind.language_kind import LanguageKind

from ..mixin.calc_cell_mixin import CalcCellMixin
from ..cell_control import CellControl
from ..ctl_prop_kind import CtlPropKind
from .ctl_provider import CtlProvider


if TYPE_CHECKING:
    from typing_extensions import override
    from com.sun.star.drawing import ControlShape  # service
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from ooodev.form.controls.form_ctl_base import FormCtlBase
    from .......___lo_pip___.config import Config
    from .....ex import CellDeletedError
    from ..ctl_t import CtlT
    from .....ex.exceptions import CustomPropertyMissingError

    from .....const.event_const import (
        CONTROL_ADDED,
        CONTROL_REMOVED,
        CONTROL_REMOVING,
        CONTROL_ADDING,
        CONTROL_UPDATING,
        CONTROL_UPDATED,
    )
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.ex.exceptions import CellDeletedError
    from libre_pythonista_lib.ex.exceptions import CustomPropertyMissingError
    from ___lo_pip___.config import Config

    from libre_pythonista_lib.const.event_const import (
        CONTROL_ADDED,
        CONTROL_REMOVED,
        CONTROL_REMOVING,
        CONTROL_ADDING,
        CONTROL_UPDATING,
        CONTROL_UPDATED,
    )

    def override(f) -> object:  # noqa: ANN001
        return f


class CtlProviderDefault(CtlProvider, LogMixin, CalcCellMixin):
    """Default Control Provider"""

    @override
    def __init__(self, ctl: CtlT) -> None:
        CtlProvider.__init__(self, ctl)
        LogMixin.__init__(self)
        CalcCellMixin.__init__(self, ctl.calc_cell)
        self._cfg = Config()
        self.is_deleted_cell = ctl.calc_cell.extra_data.get("deleted", False)
        self._script_name = f"{self._cfg.oxt_name}.oxt|python|scripts|{self._cfg.py_script_sheet_ctl_click}"
        self._script_loc = f"{self._script_name}${self._cfg.macro_lp_sheet_ctl_click}"

    @override
    def add_ctl(self) -> object | None:
        # There are bugs when accessing controls on sheets.
        # see: https://bugs.documentfoundation.org/show_bug.cgi?id=159134
        # Controls can lose there models when switched to a different sheet and back.
        # For this reason we only return the shape from them method.
        # Shape.getControl() can be used if necessary.,
        self.log.debug("add_ctl(): Entered")
        try:
            cargs = CancelEventArgs(self)
            dd = DotDict(cell=self.calc_cell, control=self)
            cargs.event_data = dd
            self.trigger_event(CONTROL_ADDING, cargs)
            if cargs.cancel:
                self.log.debug("add_ctl(): Cancelled")
                return

            if self.is_deleted_cell:
                raise CellDeletedError(f"Cell is deleted: {self.calc_cell.cell_obj}")

            # check for the shape on the draw page.
            # If for some reason the control in not found it is possible a shape was there.
            # In this case we need to remove the shape.
            with contextlib.suppress(mEx.ShapeMissingError, CustomPropertyMissingError):
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.ctl.ctl_shape_name
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug("add_ctl(): Found Shape: %s. Assuming control is in tact.", shape_name)
                self.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
                return shape.component

            name = self.ctl.ctl_name
            cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
            btn = cell_ctl.insert_control_button(label=self.ctl.get_label(), name=name)
            self.log.debug("%s: add_ctl(): Inserted Button: %s", self.__class__.__name__, name)
            shape = btn.control_shape

            self._set_size(shape)
            btn.printable = False
            btn.model.BackgroundColor = self._get_button_bg_color()  # type: ignore
            btn.tab_stop = False
            # btn.apply_styles()
            # need a way to manage the script location.
            # one possible way is to add the macro to the document and then call it.
            # Another is to loop all the controls in the sheet and update the script location.
            # Optionally the sheet can store the extension location on save. Then can be use to update controls on load if needed.
            self._set_ctl_script(btn)
            self.log.debug("%s: add_ctl(): Leaving", self.__class__.__name__)
            if self.ctl.supports_prop(CtlPropKind.CTL_SHAPE):
                self.calc_cell.set_custom_property(
                    self._get_prop_key_value(CtlPropKind.CTL_SHAPE), self.ctl.ctl_shape_name
                )
            if self.ctl.supports_prop(CtlPropKind.CTL_ORIG):
                self.calc_cell.set_custom_property(
                    self._get_prop_key_value(CtlPropKind.CTL_ORIG), str(self.ctl.control_kind)
                )
            self.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
            return shape
        except Exception as e:
            self.log.exception("add_ctl error: %s", e)
            return None

    @override
    def update_ctl_action(self) -> None:
        try:
            cargs = CancelEventArgs(self)

            cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
            ctl = cast("FormCtlBase", cell_ctl.current_control)
            dd = DotDict(cell=self.calc_cell, cell_control=cell_ctl, ctl=ctl, control=self)
            cargs.event_data = dd
            self.trigger_event(CONTROL_UPDATING, cargs)
            if cargs.cancel:
                self.log.debug("update_ctl_action(): Cancelled")
                return
            if ctl is None:
                self.log.debug("update_ctl_action(): Control not found")
                return
            # self._remove_ctl_script(ctl)
            self._set_ctl_script(ctl)
            self.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
            self.log.debug("update_ctl_action(): Script set")
        except Exception:
            self.log.exception("update_ctl_action(): Error getting current control")

    @override
    def update_ctl(self) -> None:
        self.log.debug(f"{self.__class__.__name__}: update_ctl(): Entered")
        try:
            sheet = self.calc_cell.calc_sheet
            dp = sheet.draw_page
            shape_name = self.ctl.ctl_shape_name
            cargs = CancelEventArgs(self)
            dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
            cargs.event_data = dd
            self.trigger_event(CONTROL_UPDATING, cargs)
            if cargs.cancel:
                self.log.debug("update_ctl(): Cancelled")
                return
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug("update_ctl(): Found Shape: %s", shape_name)
                self._set_size(shape.component)  # type: ignore
                self.log.debug("update_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug("update_ctl(): Shape not found: %s", shape_name)
                self.log.debug("update_ctl(): Leaving")
            self.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
        except Exception as e:
            self.log.exception("update_ctl error: %s", e)
            return None

    @override
    def remove_ctl(self) -> None:
        self.log.debug("remove_ctl(): Entered")
        try:
            sheet = self.calc_cell.calc_sheet
            dp = sheet.draw_page
            shape_name = self.ctl.ctl_shape_name

            cargs = CancelEventArgs(self)
            dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
            cargs.event_data = dd
            self.trigger_event(CONTROL_REMOVING, cargs)
            if cargs.cancel:
                self.log.debug("update_ctl(): Cancelled")
                return
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug("remove_ctl(): Found Shape: %s", shape_name)
                dp.remove(shape.component)  # type: ignore
                self.log.debug("remove_ctl(): Removed Shape: %s", shape_name)
                shape = None
                self.log.debug("remove_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug("remove_ctl(): Shape not found: %s", shape_name)
                self.log.debug("remove_ctl(): Leaving")

            if self.ctl.supports_prop(CtlPropKind.CTL_SHAPE):
                prop_key = self._get_prop_key_value(CtlPropKind.CTL_SHAPE)
                if self.calc_cell.has_custom_property(prop_key):
                    self.log.debug("remove_ctl(): Removing custom %s", prop_key)
                    self.calc_cell.remove_custom_property(prop_key)
            if self.ctl.supports_prop(CtlPropKind.CTL_ORIG):
                prop_key = self._get_prop_key_value(CtlPropKind.CTL_SHAPE)
                if self.calc_cell.has_custom_property(prop_key):
                    self.log.debug("remove_ctl(): Removing custom %s", self.__class__.__name__, prop_key)
                    self.calc_cell.remove_custom_property(prop_key)
            self.trigger_event(CONTROL_REMOVED, EventArgs.from_args(cargs))
        except Exception as e:
            self.log.error(f"{self.__class__.__name__}: remove_ctl error: {e}", exc_info=True)
            return None

    def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
        """
        Gets the position and size of the control.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
        """
        ps = self.calc_cell.component.Position
        size = self.calc_cell.component.Size
        return (ps.X, ps.Y, size.Width, size.Height)

    def _get_button_bg_color(self) -> int:
        return StandardColor.TEAL_LIGHT3

    def _set_size(self, shape: ControlShape) -> None:
        x, y, width, height = self.get_cell_pos_size()
        # sz = shape.getSize()
        new_sz = Size(min(height, int(UnitMM100(455))), height)
        # new_sz = Size(sz.Height, sz.Height)
        shape.setSize(new_sz)
        shape.setPosition(Point(x, y))

    def _set_ctl_script(self, ctl: FormCtlBase) -> None:
        """
        Sets the actionPerformed script location for the control.

        Args:
            ctl (FormCtlBase): Control that has a actionPerformed method.
        """
        location = "share:uno_packages" if self._cfg.is_shared_installed else "user:uno_packages"
        if self.log.is_debug:
            self.log.debug("set_ctl_script(): Script location: %s", location)
            self.log.debug("set_ctl_script(): Script Name: %s", self._script_loc)
        ctl.assign_script(
            interface_name=XActionListener,  # type: ignore
            method_name="actionPerformed",
            script_name=self._script_loc,
            loc=location,
            language=LanguageKind.PYTHON,
            auto_remove_existing=True,
        )

    def _get_prop_key_value(self, prop_kind: CtlPropKind) -> str:
        """
        Gets a custom property value from the cell.

        Args:
            key (CtlPropKind): Custom property key.

        Returns:
            Any: Value of the custom property.
        """
        return f"{self._cfg.cell_cp_prefix}{prop_kind.value}"
