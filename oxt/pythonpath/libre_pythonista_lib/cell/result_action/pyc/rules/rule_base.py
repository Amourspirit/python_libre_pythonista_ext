from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from .......___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class RuleBase:
    def __init__(self, cell: CalcCell, data: Any) -> None:
        self.cell = cell
        self.data = data
        self.cfg = Config()
        self.cell_prop_key = f"{self.cfg.cell_cp_prefix}modify_trigger_event"

    def get_is_match(self) -> bool:
        raise NotImplementedError

    def action(self) -> Any:
        return self.data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.cell.cell_obj}, {self.data})"
