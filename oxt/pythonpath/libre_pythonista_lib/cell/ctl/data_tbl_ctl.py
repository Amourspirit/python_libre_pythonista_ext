from __future__ import annotations
from typing import Any, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from ooodev.exceptions import ex as mEx  # noqa: N812
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from .simple_ctl import SimpleCtl
from ..state.ctl_state import CtlState
from ..state.state_kind import StateKind
from ...const.event_const import CONTROL_UPDATING, CONTROL_UPDATED


if TYPE_CHECKING:
    from com.sun.star.drawing import ControlShape  # service


class DataTblCtl(SimpleCtl):
    @override
    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_tbl_data

    @override
    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        return shape

    @override
    def _get_label(self) -> str:
        rs = self.res.resolve_string("ctl003")  # Table Data
        return f"<> {rs}"

    @override
    def _set_size(self, shape: ControlShape) -> None:
        x, y, width, height = self.get_cell_pos_size()
        shape.setSize(Size(width, height))
        shape.setPosition(Point(x, y))

    @override
    def update_ctl(self) -> None:
        """
        Updates the control state based on the current cell state.
        This method performs the following steps:

        1. Logs the entry into the method.
        2. Retrieves the current sheet and draw page.
        3. Constructs the shape name using the namer.
        4. Triggers the ``CONTROL_UPDATING`` event with relevant data.
        5. Checks if the event was cancelled and exits if so.
        6. Attempts to find the shape by name on the draw page.
        7. If the shape is found:
            - Retrieves the control state.
            - Hides the control if the state is ARRAY.
            - Shows the control and sets its size if the state is PY_OBJ.
        8. Logs the exit from the method.
        9. Triggers the ``CONTROL_UPDATED`` event.
        10. Catches and logs any exceptions that occur during the process.

        Raises:
            Exception: If any error occurs during the update process, it is logged.

        Triggers:
            CONTROL_UPDATING: Before the control is added.
            CONTROL_UPDATED: After the control has been added.

        Notes:
            Triggers are fired using the shared_event object.
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
                    self.log.debug(
                        "%s: update_ctl(): Found Shape: %s",
                        self.__class__.__name__,
                        shape_name,
                    )
                    ctl_state = CtlState(cell=self.calc_cell)
                    state = ctl_state.get_state()
                    if state == StateKind.ARRAY:
                        self.log.debug(
                            "%s: update_ctl(): State is ARRAY. Hiding Control.",
                            self.__class__.__name__,
                        )
                        shape.set_visible(False)
                    else:
                        self.log.debug(
                            "%s: update_ctl(): State is PY_OBJ. Showing control.",
                            self.__class__.__name__,
                        )
                        shape.set_visible(True)

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
