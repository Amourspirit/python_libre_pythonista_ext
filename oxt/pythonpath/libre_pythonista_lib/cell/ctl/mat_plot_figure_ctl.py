from __future__ import annotations
from typing import Any, Tuple, Set
from ooodev.calc import CalcCell
from pathlib import Path

from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..props.key_maker import KeyMaker
from ...log.log_inst import LogInst
from ...ex import CellDeletedError
from .error_ctl import ErrorCtl
from ...event.shared_event import SharedEvent


# from ..lpl_cell import LplCell
from ...code.py_source_mgr import PyInstance
from .cell_img import CellImg
from .shape_namer import ShapeNamer
from ...const.event_const import (
    CONTROL_ADDED,
    CONTROL_REMOVED,
    CONTROL_REMOVING,
    CONTROL_ADDING,
)


class MatPlotFigureCtl:
    """
    A class to represent a pyc formula result rule.
    """

    def __init__(self, calc_cell: CalcCell) -> None:
        self.calc_cell = calc_cell
        self.key_maker = KeyMaker()
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)
        self.log = LogInst()
        self._py_src = PyInstance(self.calc_cell.calc_doc)
        self.namer = ShapeNamer(self.calc_cell)
        self._prev_img = ""
        self._supported_features = None
        self.shared_event = SharedEvent(self.calc_cell.calc_doc)
        with self.log.indent(True):
            self.log.debug("%s: __init__(): Entered", self.__class__.__name__)

    def _get_features(self) -> Set[str]:
        if self._supported_features is None:
            self._supported_features = {
                "add_ctl",
                "remove_ctl",
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
        return self.key_maker.rule_names.cell_data_type_mp_figure

    def add_ctl(self) -> Any:
        """
        Adds a control to the cell.
        This method performs the following steps:

        1. Triggers the ``CONTROL_ADDING`` event.
        2. Checks if the event was cancelled.
        3. Retrieves the source data for the cell.
        4. Checks if the cell is marked as deleted and raises an error if so.
        5. Compares the current image with the previous image to determine if an update is necessary.
        6. Removes the existing control if an update is required.
        7. Inserts a new image linked to the cell.
        8. Sets the name of the shape.
        9. Triggers the ``CONTROL_ADDED`` event.

        Raises:
            CellDeletedError: If the cell is marked as deleted.
            Exception: If there is an error while setting the control script.

        Triggers:
            CONTROL_ADDING: Before the control is added.
            CONTROL_ADDED: After the control has been added.

        Notes:
            Triggers are fired using the shared_event object.
        """

        with self.log.indent(True):
            cargs = CancelEventArgs(self)
            dd = DotDict(cell=self.calc_cell, control=self)
            cargs.event_data = dd
            self.shared_event.trigger_event(CONTROL_ADDING, cargs)
            if cargs.cancel:
                self.log.debug(f"{self.__class__.__name__}: add_ctl(): Cancelled")
                return

            src = self._py_src[self.calc_cell.cell_obj]
            dot_dict = src.dd_data
            try:
                if self.is_deleted_cell:
                    raise CellDeletedError("Cell is deleted: %s", self.calc_cell.cell_obj)
                # if self.log.is_debug:
                #     for k, v in dd.items():
                #         self.log.debug(f"src DotDict: {k}: {v}")
                if self._prev_img == dot_dict.data:
                    self.log.debug("MatPlotFigureCtl: add_ctl(): No change in image. Not adding again.")
                    return
                self.remove_ctl()
                svg_path = Path(dot_dict.data)
                if not svg_path.exists():
                    self.log.error("MatPlotFigureCtl: add_ctl(): File not found: %s", svg_path)
                    return
                ci = CellImg(self.calc_cell, self.calc_cell.lo_inst)
                shp = ci.insert_cell_image_linked(svg_path)
                shp.name = self.namer.shape_name  # type: ignore

                # self._set_ctl_script(ctl)
                self.log.debug("MatPlotFigureCtl: set_ctl_script(): Script set")

                self.shared_event.trigger_event(CONTROL_ADDED, EventArgs.from_args(cargs))
            except Exception:
                self.log.exception("MatPlotFigureCtl: set_ctl_script(): Error getting current control")

    def remove_ctl(self):
        """
        Removes the control associated with the current cell.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the sheet and draw page from the current cell.
        3. Triggers the CONTROL_REMOVING event with relevant data.
        4. Checks if the event was cancelled and exits if so.
        5. Attempts to find and remove the shape associated with the control.
        6. Logs the removal of the shape or logs if the shape was not found.
        7. Removes custom properties associated with the control from the cell.
        8. Triggers the CONTROL_REMOVED event.
        9. Handles any exceptions that occur during the process and logs them.
        10. Checks for and removes any error control that may have been added.

        Returns:
            None:

        Triggers:
            CONTROL_REMOVING: Before the control is removed.
            CONTROL_REMOVED: After the control has been inserted.

        Note:
            Triggers are fired using the shared_event object.
        """

        with self.log.indent(True):
            self.log.debug(f"{self.__class__.__name__}: remove_ctl(): Entered")
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.shape_name
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
                    return None

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
                self.log.error(
                    "%s: remove_ctl error: %s",
                    self.__class__.__name__,
                    e,
                    exc_info=True,
                )
                return None

            # an error control may have been added. Remove it.
            try:
                self.log.debug(
                    "%s: remove_ctl(): Checking for error control.",
                    self.__class__.__name__,
                )
                err_ctl = ErrorCtl(self.calc_cell)
                err_ctl.remove_ctl()
            except Exception:
                self.log.debug(
                    "%s: remove_ctl(): Error removing error control. May not have been an error control to remove.",
                    self.__class__.__name__,
                )

    def update_ctl(self) -> None:
        """Updates the control. Usually set the controls size and pos."""
        pass

    def get_cell_pos_size(self) -> Tuple[int, int, int, int]:
        """
        Gets the position and size of the control.

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) in  ``1/100th mm``.
        """
        ps = self.calc_cell.component.Position
        size = self.calc_cell.component.Size
        return (ps.X, ps.Y, size.Width, size.Height)

    def update_ctl_action(self) -> None:
        """
        Updates the controls action such as setting ``actionPerformed`` macro.
        """
        pass
