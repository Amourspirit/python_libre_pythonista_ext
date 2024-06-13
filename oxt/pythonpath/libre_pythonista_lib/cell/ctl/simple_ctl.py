from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from ooodev.events.args.event_args import EventArgs
from ooodev.calc import CalcCell
from ooodev.units import UnitMM100
from ooodev.exceptions import ex as mEx
from ooo.dyn.awt.size import Size
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service


class SimpleCtl:
    def __init__(self, event: EventArgs):
        """
        Constructor

        Args:
            event (EventArgs): Event data for when a cell custom property is modified.

        Note:
            ``event.event_data`` is a DotDict with the following keys:
            - absolute_name: str
            - event_obj: ``com.sun.star.lang.EventObject``
            - code_name: str
            - trigger_name: str
            - remove_custom_property: bool
            - calc_cell: CalcCell
            - cell_cp_codename: Unique code name for cell custom property
        """
        self.log = LogInst()
        self.event_data = event.event_data

    def add_ctl(self) -> Any:
        self.log.debug(f"SimpleCtl: add_ctl(): Entered")
        try:
            cell = cast("CalcCell", self.event_data.calc_cell)
            sheet = cell.calc_sheet
            dp = sheet.draw_page
            name = f"ctl_{self.event_data.code_name}"
            shape_name = f"SHAPE_{name}"
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(f"SimpleCtl: add_ctl(): Found Shape: {shape_name}")
                dp.remove(shape.component)  # type: ignore
                self.log.debug(f"SimpleCtl: add_ctl(): Removed Shape: {shape_name}")
                shape = None
            except mEx.ShapeMissingError:
                self.log.debug(f"SimpleCtl: add_ctl(): Shape not found: {shape_name}")

            btn = cell.control.insert_control_button(label="<>", name=name)
            self.log.debug(f"SimpleCtl: add_ctl(): Inserted Button: {name}")
            shape = btn.control_shape
            props = {"Anchor": cell.component, "ResizeWithCell": True, "MoveProtect": False}
            for key, value in props.items():
                setattr(shape, key, value)
            sz = shape.getSize()
            new_sz = Size(sz.Height, sz.Height)
            shape.setSize(new_sz)
            btn.printable = False
            self.log.debug(f"SimpleCtl: add_ctl(): Leaving")
            return btn
        except Exception as e:
            self.log.error(f"SimpleCtl: add_ctl error: {e}", exc_info=True)
            return None

    def remove_ctl(self):
        self.log.debug(f"SimpleCtl: remove_ctl(): Entered")
        try:
            cell = cast("CalcCell", self.event_data.calc_cell)
            sheet = cell.calc_sheet
            dp = sheet.draw_page
            name = f"ctl_{self.event_data.code_name}"
            shape_name = f"shape_{name}"
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(f"SimpleCtl: remove_ctl(): Found Shape: {shape_name}")
                dp.remove(shape)  # type: ignore
                self.log.debug(f"SimpleCtl: remove_ctl(): Removed Shape: {shape_name}")
                shape = None
                self.log.debug(f"SimpleCtl: remove_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug(f"SimpleCtl: remove_ctl(): Shape not found: {shape_name}")
                self.log.debug(f"SimpleCtl: remove_ctl(): Leaving")

        except Exception as e:
            self.log.error(f"SimpleCtl: remove_ctl error: {e}", exc_info=True)
            return None
