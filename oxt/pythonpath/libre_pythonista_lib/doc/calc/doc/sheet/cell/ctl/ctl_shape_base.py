from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from ooodev.utils.color import Color
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase

    Color = int


class CtlShapeBase(CtlBase):
    # region Properties

    @property
    def shape_name(self) -> str:
        """Gets the control shape name."""
        return self.ctl.ctl_shape_name

    @property
    def label(self) -> str:
        """Gets the control label such as ``<>``."""
        return self.ctl.label

    @property
    def background_color(self) -> Color:
        """Gets the background color of the control."""
        return self.ctl.ctl_bg_color

    @property
    def control(self) -> Any:  # noqa: ANN401
        """Gets the control for the cell or None if it does not exist."""
        return self.ctl.control

    # endregion Properties
