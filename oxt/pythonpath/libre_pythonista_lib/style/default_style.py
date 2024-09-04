from __future__ import annotations
from ooodev.calc import CalcCellRange, CalcCell
from ooodev.utils.color import StandardColor
from ooodev.format.calc.direct.cell.borders import Side, Shadow


class DefaultStyle:
    """Manages formatting of Ranges."""

    def __init__(self):
        pass

    def _get_border_side(self) -> Side:
        side = Side(color=StandardColor.TEAL_LIGHT2)
        return side

    def _get_border_shadow(self) -> Shadow:
        shadow = Shadow(color=StandardColor.TEAL_LIGHT1, width=1)
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
