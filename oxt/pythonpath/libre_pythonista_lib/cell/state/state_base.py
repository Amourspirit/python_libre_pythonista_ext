from __future__ import annotations
from typing import Any
from ooodev.calc import CalcCell
from ..props.key_maker import KeyMaker


class StateBase:
    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._key_maker = KeyMaker()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(cell={self.cell.cell_obj})>"

    def get_state(self) -> Any:
        raise NotImplementedError

    def set_state(self, value: Any) -> None:
        self.cell.set_custom_property(self.key_maker.ctl_state_key, value)

    # region properties
    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def key_maker(self) -> KeyMaker:
        return self._key_maker

    # endregion properties
