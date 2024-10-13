from __future__ import annotations
from typing import Any, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
from ooo.dyn.awt.size import Size
from ooo.dyn.awt.point import Point
from ooodev.exceptions import ex as mEx

from .simple_ctl import SimpleCtl
from ..state.ctl_state import CtlState
from ..state.state_kind import StateKind


if TYPE_CHECKING:
    from com.sun.star.drawing import ControlShape  # service


class DataSeriesCtl(SimpleCtl):

    @override
    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_pd_series

    @override
    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        return shape

    @override
    def _get_label(self) -> str:
        rs = self.res.resolve_string("ctl002")  # DataFrame
        return f"<> {rs}"

    @override
    def _set_size(self, shape: ControlShape) -> None:
        x, y, width, height = self.get_cell_pos_size()
        shape.setSize(Size(width, height))
        shape.setPosition(Point(x, y))

    @override
    def update_ctl(self) -> None:
        with self.log.indent(True):
            self.log.debug(f"{self.__class__.__name__}: update_ctl(): Entered")
            try:
                sheet = self.calc_cell.calc_sheet
                dp = sheet.draw_page
                shape_name = self.namer.ctl_shape_name

                try:
                    shape = dp.find_shape_by_name(shape_name)
                    self.log.debug(f"{self.__class__.__name__}: update_ctl(): Found Shape: {shape_name}")
                    ctl_state = CtlState(cell=self.calc_cell)
                    state = ctl_state.get_state()
                    if state == StateKind.ARRAY:
                        self.log.debug(f"{self.__class__.__name__}: update_ctl(): State is ARRAY. Hiding Control.")
                        shape.set_visible(False)
                    else:
                        self.log.debug(f"{self.__class__.__name__}: update_ctl(): State is PY_OBJ. Showing control.")
                        shape.set_visible(True)

                        self._set_size(shape.component)  # type: ignore
                    self.log.debug(f"{self.__class__.__name__}: update_ctl(): Leaving")
                except mEx.ShapeMissingError:
                    self.log.debug(f"{self.__class__.__name__}: update_ctl(): Shape not found: {shape_name}")
                    self.log.debug(f"{self.__class__.__name__}: update_ctl(): Leaving")

            except Exception as e:
                self.log.error(f"{self.__class__.__name__}: update_ctl error: {e}", exc_info=True)
                return None
