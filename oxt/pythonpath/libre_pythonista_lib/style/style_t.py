from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.utils.color import Color
else:
    Color = int


class StyleT(Protocol):
    """A protocol for style objects."""

    # def add_style_range(self, cell_range: CalcCellRange) -> None:
    #     """Formats a cell range."""
    #     ...
    # def add_style_cell(self, cell: CalcCell) -> None:
    #     """Formats a cell."""
    #     ...
    # def remove_style_range(self, cell_range: CalcCellRange) -> None:
    #     """Removes formatting from a cell range."""
    #     ...
    # def remove_style_cell(self, cell: CalcCell) -> None:
    #     """Removes formatting from a cell."""
    #     ...

    @property
    def color_main(self) -> Color: ...

    @property
    def color_border(self) -> Color: ...

    @property
    def color_shadow(self) -> Color: ...

    @property
    def color_error(self) -> Color: ...
