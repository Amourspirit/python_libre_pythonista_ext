from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Tuple, Set
import contextlib
import uno
from com.sun.star.awt import XActionListener
from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point

from ooodev.calc import CalcCell
from ooodev.units import UnitMM100
from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.utils.kind.language_kind import LanguageKind
from ooodev.utils.color import StandardColor
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from .ctl_namer import CtlNamer
from .cell_control import CellControl
from ...ex import CellDeletedError
from ...log.log_inst import LogInst
from ...res.res_resolver import ResResolver
from ..props.key_maker import KeyMaker
from ...event.shared_event import SharedEvent

from ...const.event_const import (
    CONTROL_ADDED,
    CONTROL_REMOVED,
    CONTROL_REMOVING,
    CONTROL_ADDING,
    CONTROL_UPDATING,
    CONTROL_UPDATED,
)

if TYPE_CHECKING:
    from com.sun.star.drawing import ControlShape  # service
    from ooodev.form.controls.form_ctl_base import FormCtlBase
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
        self._cfg = Config()
        self._script_name = f"{self._cfg.oxt_name}.oxt|python|scripts|{self._cfg.py_script_sheet_ctl_click}"
        self._script_loc = f"{self._script_name}${self._cfg.macro_lp_sheet_ctl_click}"

        self._ctl_rule_key = self._cfg.cell_cp_prefix + "ctl_rule"
        self.calc_cell = calc_cell
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)
        self._supported_features = None
        self.log = LogInst()
        self.namer = CtlNamer(calc_cell)
        self.res = ResResolver()
        self.key_maker = KeyMaker()
        self.shared_event = SharedEvent(self.calc_cell.calc_doc)

    def _get_features(self) -> Set[str]:
        if self._supported_features is None:
            self._supported_features = {
                "add_ctl",
                "remove_ctl",
                "update_ctl",
                "update_ctl_action",
                "get_rule_name",
                "get_cell_pos_size",
            }

        return self._supported_features

    def supports_feature(self, feature: str) -> bool:
        """
        Checks if the feature is supported.

        Args:
            feature (str): Feature to check such as "update_ctl", "add_ctl", "remove_ctl", "update_ctl_action", "get_rule_name", "get_cell_pos_size".

        Returns:
            bool: True if supported, False otherwise.
        """
        features = self._get_features()
        return feature in features

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_simple_ctl

    def update_ctl_action(self) -> None:
        """
        Updates the control action for the current cell.
        This method performs the following steps:

        1. Creates a ``CancelEventArgs`` instance for the current context.
        2. Initializes a ``CellControl`` instance for the current cell.
        3. Casts the current control to ``FormCtlBase``.
        4. Creates a ``DotDict`` containing relevant data for the event.
        5. Triggers the ``CONTROL_UPDATING`` event with the created ``CancelEventArgs``.
        6. Checks if the event was cancelled and logs a debug message if so.
        7. Checks if the control is `None` and logs a debug message if so.
        8. Sets the control script using ``_set_ctl_script``.
        9. Triggers the ``CONTROL_UPDATED`` event with the updated event arguments.
        10. Logs a debug message indicating the script has been set.

        Exception Handling:
            - Logs an exception message if an error occurs while getting the current control.

        Triggers:
            CONTROL_UPDATING: Before the control is updated.
            CONTROL_UPDATED: After the control has been updated.

        Note:
            - Triggers are fired using the shared_event object
        """

        with self.log.indent(True):
            try:
                cargs = CancelEventArgs(self)

                cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
                ctl = cast("FormCtlBase", cell_ctl.current_control)
                dd = DotDict(cell=self.calc_cell, cell_control=cell_ctl, ctl=ctl, control=self)
                cargs.event_data = dd
                self.shared_event.trigger_event(CONTROL_UPDATING, cargs)
                if cargs.cancel:
                    self.log.debug(f"{self.__class__.__name__}: update_ctl_action(): Cancelled")
                    return
                if ctl is None:
                    self.log.debug("SimpleCtl: update_ctl_action(): Control not found")
                    return
                # self._remove_ctl_script(ctl)
                self._set_ctl_script(ctl)
                self.shared_event.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
                self.log.debug("SimpleCtl: update_ctl_action(): Script set")
            except Exception:
                self.log.exception("SimpleCtl: update_ctl_action(): Error getting current control")

    def _set_ctl_script(self, ctl: FormCtlBase) -> None:
        """
        Sets the actionPerformed script location for the control.

        Args:
            ctl (FormCtlBase): Control that has a actionPerformed method.
        """
        if self._cfg.is_shared_installed:
            location = "share:uno_packages"
        else:
            location = "user:uno_packages"
        if self.log.is_debug:
            self.log.debug(f"SimpleCtl: set_ctl_script(): Script location: {location}")
            self.log.debug(f"SimpleCtl: set_ctl_script(): Script Name: {self._script_loc}")
        ctl.assign_script(
            interface_name=XActionListener,  # type: ignore
            method_name="actionPerformed",
            script_name=self._script_loc,
            loc=location,
            language=LanguageKind.PYTHON,
            auto_remove_existing=True,
        )

    def add_ctl(self) -> Any:
        """
        Adds a control to the cell.
        This method handles the addition of a control to a cell, including the creation of the control button,
        setting its properties, and managing events related to the control addition. Due to known bugs with
        accessing controls on sheets, this method only returns the shape of the control. The shape's control
        can be accessed using ``Shape.getControl()`` if necessary.

        Returns:
            Any: The shape of the control added to the cell, or None if an error occurs or the operation is cancelled.

        Raises:
            CellDeletedError: If the cell has been deleted.

        Triggers:
            CONTROL_ADDING: Before the control is added.
            CONTROL_ADDED: After the control has been added.

        Notes:
            - Controls can lose their models when switched to a different sheet and back.
            - If the control is not found, any existing shape is removed.
            - The method logs various debug information and triggers events during the control addition process.
            - Triggers are fired using the shared_event object.
        """

        # There are bugs when accessing controls on sheets.
        # see: https://bugs.documentfoundation.org/show_bug.cgi?id=159134
        # Controls can lose there models when switched to a different sheet and back.
        # For this reason we only return the shape from them method.
        # Shape.getControl() can be used if necessary.,
        with self.log.indent(True):
            self.log.debug(f"{self.__class__.__name__}: add_ctl(): Entered")
            try:
                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, control=self)
                cargs.event_data = dd
                self.shared_event.trigger_event(CONTROL_ADDING, cargs)
                if cargs.cancel:
                    self.log.debug(f"{self.__class__.__name__}: add_ctl(): Cancelled")
                    return

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
                        "%s: add_ctl(): Found Shape: %s. Assuming control is in tact.",
                        self.__class__.__name__,
                        shape_name,
                    )
                    self.shared_event.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
                    return shape.component

                name = self.namer.ctl_name
                cell_ctl = CellControl(self.calc_cell, self.calc_cell.lo_inst)
                # current_control = cell_ctl.current_control
                # if current_control is not None:
                #     self.log.debug(f"SimpleCtl: add_ctl(): Current Control Found: {name}")
                #     return current_control

                # self.log.debug(f"SimpleCtl: add_ctl(): Current Control Not Found: {name}")

                btn = cell_ctl.insert_control_button(label=self._get_label(), name=name)
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
                self.calc_cell.set_custom_property(self.key_maker.ctl_shape_key, self.namer.ctl_shape_name)
                self.calc_cell.set_custom_property(self.key_maker.ctl_orig_ctl_key, self.get_rule_name())
                self.shared_event.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
                return shape
            except Exception as e:
                self.log.error(f"{self.__class__.__name__}: add_ctl error: {e}", exc_info=True)
                return None

    def update_ctl(self) -> None:
        """
        Updates the control by finding the associated shape in the draw page and setting its size.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the sheet and draw page from the calc cell.
        3. Gets the shape name from the namer.
        4. Creates a CancelEventArgs object and triggers the ``CONTROL_UPDATING`` event.
        5. If the event is cancelled, logs the cancellation and exits.
        6. Attempts to find the shape by its name in the draw page.
        7. If the shape is found, sets its size and logs the success.
        8. If the shape is not found, logs the missing shape.
        9. Triggers the ``CONTROL_UPDATED`` event.
        10. Catches and logs any exceptions that occur during the process.

        Raises:
            Exception: If any error occurs during the update process, it is logged.

        Triggers:
            CONTROL_UPDATING: Before the control is updated.
            CONTROL_UPDATED: After the control has been updated.

        Note:
            Triggers are fired using the shared_event object
        """

        with self.log.indent(True):
            self.log.debug(f"{self.__class__.__name__}: update_ctl(): Entered")
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.ctl_shape_name
                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
                cargs.event_data = dd
                self.shared_event.trigger_event(CONTROL_UPDATING, cargs)
                if cargs.cancel:
                    self.log.debug("%s: update_ctl(): Cancelled", self.__class__.__name__)
                    return
                try:
                    shape = dp.find_shape_by_name(shape_name)
                    self.log.debug(f"{self.__class__.__name__}: update_ctl(): Found Shape: {shape_name}")
                    self._set_size(shape.component)  # type: ignore
                    self.log.debug("%s: update_ctl(): Leaving", self.__class__.__name__)
                except mEx.ShapeMissingError:
                    self.log.debug(
                        "%s: update_ctl(): Shape not found: %s",
                        self.__class__.__name__,
                        shape_name,
                    )
                    self.log.debug("%s: update_ctl(): Leaving", self.__class__.__name__)
                self.shared_event.trigger_event(CONTROL_UPDATED, EventArgs.from_args(cargs))
            except Exception as e:
                self.log.error(
                    "%s: update_ctl error: %s",
                    self.__class__.__name__,
                    e,
                    exc_info=True,
                )
                return None

    def _get_button_bg_color(self) -> int:
        return StandardColor.TEAL_LIGHT3

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
        """
        Removes a control from the LibreOffice Calc sheet.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the sheet and draw page from the calc cell.
        3. Constructs the shape name using the namer.
        4. Triggers the ``CONTROL_REMOVING`` event with relevant data.
        5. If the event is not canceled, attempts to find and remove the shape by name.
        6. Logs the success or failure of shape removal.
        7. Removes custom properties related to the control from the calc cell.
        8. Triggers the ``CONTROL_REMOVED`` event after successful removal.

        If an exception occurs during the process, it logs the error.

        Raises:
            Exception: If any error occurs during the removal process.

        Returns:
            None:

        Triggers:
            CONTROL_REMOVING: Before the control is removed.
            CONTROL_REMOVED: After the control has been inserted.

        Note:
            Triggers are fired using the shared_event object.
        """

        with self.log.indent(True):
            self.log.debug("%s: remove_ctl(): Entered", self.__class__.__name__)
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.ctl_shape_name

                cargs = CancelEventArgs(self)
                dd = DotDict(cell=self.calc_cell, shape_name=shape_name, control=self)
                cargs.event_data = dd
                self.shared_event.trigger_event(CONTROL_REMOVING, cargs)
                if cargs.cancel:
                    self.log.debug("%s: update_ctl(): Cancelled", self.__class__.__name__)
                    return
                try:
                    shape = dp.find_shape_by_name(shape_name)
                    self.log.debug(
                        "%s: remove_ctl(): Found Shape: %s",
                        self.__class__.__name__,
                        shape_name,
                    )
                    dp.remove(shape.component)  # type: ignore
                    self.log.debug(
                        "%s: remove_ctl(): Removed Shape: %s",
                        self.__class__.__name__,
                        shape_name,
                    )
                    shape = None
                    self.log.debug("%s: remove_ctl(): Leaving", self.__class__.__name__)
                except mEx.ShapeMissingError:
                    self.log.debug(
                        "%s: remove_ctl(): Shape not found: %s",
                        self.__class__.__name__,
                        shape_name,
                    )
                    self.log.debug("%s: remove_ctl(): Leaving", self.__class__.__name__)

                if self.calc_cell.has_custom_property(self.key_maker.ctl_shape_key):
                    self.log.debug(
                        "%s: remove_ctl(): Removing custom %s",
                        self.__class__.__name__,
                        self.key_maker.ctl_shape_key,
                    )
                    self.calc_cell.remove_custom_property(self.key_maker.ctl_shape_key)
                if self.calc_cell.has_custom_property(self.key_maker.ctl_orig_ctl_key):
                    self.log.debug(
                        "%s: remove_ctl(): Removing custom %s",
                        self.__class__.__name__,
                        self.key_maker.ctl_orig_ctl_key,
                    )
                    self.calc_cell.remove_custom_property(self.key_maker.ctl_orig_ctl_key)
                self.shared_event.trigger_event(CONTROL_REMOVED, EventArgs.from_args(cargs))
            except Exception as e:
                self.log.error(f"{self.__class__.__name__}: remove_ctl error: {e}", exc_info=True)
                return None
