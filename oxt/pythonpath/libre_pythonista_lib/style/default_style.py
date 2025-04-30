from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcCellRange, CalcCell
from ooodev.utils.color import StandardColor
from ooodev.format.calc.direct.cell.borders import Side, Shadow

if TYPE_CHECKING:
    from ooodev.utils.color import Color
    from oxt.pythonpath.libre_pythonista_lib.style.style_t import StyleT
else:
    from libre_pythonista_lib.style.style_t import StyleT

    Color = int


class DefaultStyle(StyleT):
    """Manages formatting of Ranges."""

    def _get_border_side(self) -> Side:
        side = Side(color=self.color_border)
        return side

    def _get_border_shadow(self) -> Shadow:
        shadow = Shadow(color=self.color_shadow, width=1)
        return shadow

    def add_style_range(self, cell_range: CalcCellRange) -> None:
        """Formats a cell range."""
        cell_range.style_borders(border_side=self._get_border_side(), shadow=self._get_border_shadow())

    def add_style_cell(self, cell: CalcCell) -> None:
        """Formats a cell."""
        cell.style_borders(border_side=self._get_border_side(), shadow=self._get_border_shadow())

    def remove_style_range(self, cell_range: CalcCellRange) -> None:
        """Removes formatting from a cell range."""
        cell_range.style_borders_clear()

    def remove_style_cell(self, cell: CalcCell) -> None:
        """Removes formatting from a cell."""
        cell.style_borders_clear()

    @property
    def color_main(self) -> Color:
        return StandardColor.TEAL_LIGHT3

    @property
    def color_border(self) -> Color:
        return StandardColor.TEAL_LIGHT2

    @property
    def color_shadow(self) -> Color:
        return StandardColor.TEAL_LIGHT1

    @property
    def color_error(self) -> Color:
        return StandardColor.RED_LIGHT3
