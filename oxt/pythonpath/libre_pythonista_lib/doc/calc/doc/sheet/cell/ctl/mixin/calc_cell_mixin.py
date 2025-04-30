from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell


class CalcCellMixin:
    def __init__(self, calc_cell: CalcCell) -> None:
        self.__calc_cell = calc_cell

    @property
    def calc_cell(self) -> CalcCell:
        return self.__calc_cell

    @calc_cell.setter
    def calc_cell(self, value: CalcCell) -> None:
        self.__calc_cell = value
