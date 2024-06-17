from __future__ import annotations
from typing import Any, TYPE_CHECKING, Tuple
import contextlib
import uno
from com.sun.star.awt import XActionListener
from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from ooodev.calc import CalcCell
from ooodev.units import UnitMM100
from ooodev.exceptions import ex as mEx
from ooodev.utils.kind.language_kind import LanguageKind
from ooodev.utils.color import StandardColor
from .ctl_namer import CtlNamer
from .cell_control import CellControl
from ...ex import CellDeletedError
from ...log.log_inst import LogInst
from ...res.res_resolver import ResResolver

if TYPE_CHECKING:
    from com.sun.star.drawing import ControlShape  # service
    from .....___lo_pip___.config import Config

else:
    from ___lo_pip___.config import Config


class SimpleCtl:
    def __init__(self, calc_cell: CalcCell):
        """
        Constructor

        Args:
            calc_cell (CalcCell): CalcCell object.

        Raises:
            CustomPropertyMissingError: Custom Property not found
        """
        self._script_name = "LibrePythonista.oxt|python|scripts|control_handler.py"
        self._script_loc = f"{self._script_name}$on_btn_action_preformed"
        self._cfg = Config()

        self._ctl_rule_key = self._cfg.cell_cp_prefix + "ctl_rule"
        self.calc_cell = calc_cell
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)
        self.log = LogInst()
        self.namer = CtlNamer(calc_cell)
        self.res = ResResolver()

    def add_ctl(self) -> Any:
        """
        Adds a control to the cell if it does not already exist.

        Raises:
            CellDeletedError: If cell has been Deleted

        Returns:
            Any: Control Shape or None.
        """
        # There are bugs when accessing controls on sheets.
        # see: https://bugs.documentfoundation.org/show_bug.cgi?id=159134
        # Controls can lose there models when switched to a different sheet and back.
        # For this reason we only return the shape from them method.
        # Shape.getControl() can be used if necessary.,
        self.log.debug(f"{self.__class__.__name__}: add_ctl(): Entered")
        try:
            if self.is_deleted_cell:
                raise CellDeletedError(f"Cell is deleted: {self.calc_cell.cell_obj}")

            # check for the shape on the draw page.
            # If for some reason the control in not found it is possible a shape was there.
            # In this case we need to remove the shape.
            with contextlib.suppress(mEx.ShapeMissingError):
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.ctl_shape_name
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(
                    f"{self.__class__.__name__}: add_ctl(): Found Shape: {shape_name}. Assuming control is in tact."
                )

                return shape.component

            name = self.namer.ctl_name
            cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
            # current_control = cell_ctl.current_control
            # if current_control is not None:
            #     self.log.debug(f"SimpleCtl: add_ctl(): Current Control Found: {name}")
            #     return current_control

            # self.log.debug(f"SimpleCtl: add_ctl(): Current Control Not Found: {name}")

            btn = cell_ctl.insert_control_button(label=self._get_label(), name=name)
            self.log.debug(f"{self.__class__.__name__}: add_ctl(): Inserted Button: {name}")
            shape = btn.control_shape

            self._set_size(shape)
            btn.printable = False
            btn.model.BackgroundColor = StandardColor.TEAL_LIGHT3  # type: ignore
            btn.tab_stop = False
            # btn.apply_styles()
            btn.assign_script(
                interface_name=XActionListener,  # type: ignore
                method_name="actionPerformed",
                script_name=self._script_loc,
                loc="user:uno_packages",
                language=LanguageKind.PYTHON,
            )
            # self.calc_cell.set_custom_property("CTL", "1")
            self.log.debug(f"{self.__class__.__name__}: add_ctl(): Leaving")
            return shape
        except Exception as e:
            self.log.error(f"{self.__class__.__name__}: add_ctl error: {e}", exc_info=True)
            return None

    def update_ctl(self) -> None:
        self.log.debug(f"{self.__class__.__name__}: update_ctl(): Entered")
        try:
            sheet = self.calc_cell.calc_sheet
            dp = sheet.draw_page
            shape_name = self.namer.ctl_shape_name
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(f"{self.__class__.__name__}: update_ctl(): Found Shape: {shape_name}")
                self._set_size(shape.component)  # type: ignore
                self.log.debug(f"{self.__class__.__name__}: update_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug(f"{self.__class__.__name__}: update_ctl(): Shape not found: {shape_name}")
                self.log.debug(f"{self.__class__.__name__}: update_ctl(): Leaving")

        except Exception as e:
            self.log.error(f"{self.__class__.__name__}: update_ctl error: {e}", exc_info=True)
            return None

    def _set_size(self, shape: ControlShape) -> None:
        x, y, width, height = self.get_cell_pos_size()
        # sz = shape.getSize()
        new_sz = Size(min(height, int(UnitMM100(455))), height)
        # new_sz = Size(sz.Height, sz.Height)
        shape.setSize(new_sz)
        shape.setPosition(Point(x, y))

    def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
        """
        Gets the position and size of the control.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
        """
        ps = self.calc_cell.component.Position
        size = self.calc_cell.component.Size
        return (ps.X, ps.Y, size.Width, size.Height)

    def _get_label(self) -> str:
        return "<>"

    def remove_ctl(self):
        self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Entered")
        try:
            sheet = self.calc_cell.calc_sheet
            dp = sheet.draw_page
            shape_name = self.namer.ctl_shape_name
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Found Shape: {shape_name}")
                dp.remove(shape.component)  # type: ignore
                self.log.debug(f"SimpleCtl: remove_ctl(): Removed Shape: {shape_name}")
                shape = None
                self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Shape not found: {shape_name}")
                self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Leaving")

        except Exception as e:
            self.log.error(f"{self.__class__.__name__}: remove_ctl error: {e}", exc_info=True)
            return None
