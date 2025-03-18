from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from ooodev.utils.data_type.cell_obj import CellObj


class ModuleStateItem:
    def __init__(self, cell_obj: CellObj, mod_dict: Dict[str, Any], runtime_uid: str) -> None:
        self.cell_obj = cell_obj.copy()
        self.mod_dict = mod_dict
        self.runtime_uid = runtime_uid
        self.dd_data = DotDict(data=self.mod_dict.get("_"), cell_obj=cell_obj.copy(), runtime_uid=runtime_uid)
