from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib
import uno
from com.sun.star.awt import XActionListener
from ooo.dyn.awt.size import Size
from ooodev.calc import CalcCell
from ooodev.units import UnitMM100
from ooodev.exceptions import ex as mEx
from ooodev.utils.kind.language_kind import LanguageKind
from ...log.log_inst import LogInst
from ...ex import CustomPropertyMissingError
from .cell_control import CellControl
from ...ex import CellDeletedError

if TYPE_CHECKING:
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class SimpleCtl:
    def __init__(self, calc_cell: CalcCell):
        """
        Constructor

        Args:
            event (EventArgs): Event data for when a cell custom property is modified.

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
        if self.is_deleted_cell:
            self.code_name = calc_cell.extra_data.code_name
        else:
            if calc_cell.has_custom_property(self._cfg.cell_cp_codename):
                self.code_name = calc_cell.get_custom_property(self._cfg.cell_cp_codename)
            else:
                self.log.error(f"SimpleCtl: __init__(): Custom Property not found: {self._cfg.cell_cp_codename}")
                raise CustomPropertyMissingError(f"Custom Property not found: {self._cfg.cell_cp_codename}")

    def _get_control_name(self) -> str:
        return f"{self._cfg.general_code_name}_ctl_cell_{self.code_name}"

    def _get_ctl_shape_name(self) -> str:
        return f"SHAPE_{self._get_control_name()}"

    def add_ctl(self) -> Any:
        self.log.debug(f"SimpleCtl: add_ctl(): Entered")
        try:
            if self.is_deleted_cell:
                raise CellDeletedError(f"Cell is deleted: {self.calc_cell.cell_obj}")

            name = self._get_control_name()
            cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
            current_control = cell_ctl.current_control
            if current_control is not None:
                self.log.debug(f"SimpleCtl: add_ctl(): Current Control Found: {name}")
                return current_control

            self.log.debug(f"SimpleCtl: add_ctl(): Current Control Not Found: {name}")
            # check for the shape on the draw page. This is a edge case.
            # If for some reason the control in not found it is possible a shape was there.
            # In this case we need to remove the shape.
            with contextlib.suppress(mEx.ShapeMissingError):
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self._get_ctl_shape_name()
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(
                    f"SimpleCtl: add_ctl(): Found Shape: {shape_name} even though current_control is None. Removing."
                )
                dp.remove(shape.component)  # type: ignore
                self.log.debug(f"SimpleCtl: add_ctl(): Removed Shape: {shape_name}")
                shape = None

            btn = cell_ctl.insert_control_button(label="<>", name=name)
            self.log.debug(f"SimpleCtl: add_ctl(): Inserted Button: {name}")
            shape = btn.control_shape

            sz = shape.getSize()
            new_sz = Size(max(sz.Height, int(UnitMM100(455))), sz.Height)
            # new_sz = Size(sz.Height, sz.Height)
            shape.setSize(new_sz)
            btn.printable = False
            btn.assign_script(
                interface_name=XActionListener,  # type: ignore
                method_name="actionPerformed",
                script_name=self._script_loc,
                loc="user:uno_packages",
                language=LanguageKind.PYTHON,
            )
            self.calc_cell.set_custom_property("CTL", "1")
            self.log.debug(f"SimpleCtl: add_ctl(): Leaving")
            return btn
        except Exception as e:
            self.log.error(f"SimpleCtl: add_ctl error: {e}", exc_info=True)
            return None

    def remove_ctl(self):
        self.log.debug(f"SimpleCtl: remove_ctl(): Entered")
        try:
            sheet = self.calc_cell.calc_sheet
            dp = sheet.draw_page
            # name = f"ctl_{self.code_name}"
            shape_name = self._get_ctl_shape_name()
            try:
                shape = dp.find_shape_by_name(shape_name)
                self.log.debug(f"SimpleCtl: remove_ctl(): Found Shape: {shape_name}")
                dp.remove(shape.component)  # type: ignore
                self.log.debug(f"SimpleCtl: remove_ctl(): Removed Shape: {shape_name}")
                shape = None
                self.log.debug(f"SimpleCtl: remove_ctl(): Leaving")
            except mEx.ShapeMissingError:
                self.log.debug(f"SimpleCtl: remove_ctl(): Shape not found: {shape_name}")
                self.log.debug(f"SimpleCtl: remove_ctl(): Leaving")

        except Exception as e:
            self.log.error(f"SimpleCtl: remove_ctl error: {e}", exc_info=True)
            return None
