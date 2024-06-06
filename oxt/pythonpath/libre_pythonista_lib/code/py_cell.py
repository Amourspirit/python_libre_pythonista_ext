"""
Class that manages cell code.
"""

from __future__ import annotations
import uno
from ooodev.calc import CalcCell
from ooodev.utils import gen_util as gUtil
from ooodev.utils.helper.dot_dict import DotDict
from .cell_code_storage import CellCodeStorage


class PyCell:
    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._prop_prefix = "libre_pythonista_"
        self._props = self._get_properties()
        self._storage = CellCodeStorage(self)

    def _get_properties(self) -> DotDict:
        if self._cell.has_custom_properties():
            props = self._cell.get_custom_properties()
        else:
            props = DotDict()
        return props

    def _set_code_id(self) -> None:
        key = f"{self._prop_prefix}codename"
        str_id = "id_" + gUtil.Util.generate_random_alpha_numeric(14)
        self._cell.set_custom_property(key, str_id)
        setattr(self._props, key, str_id)
        return None

    def has_code(self) -> bool:
        key = f"{self._prop_prefix}codename"
        if key not in self._props:
            return False
        return self._storage.has_code()

    def save_code(self, code: str) -> None:
        self._storage.save_code(code)
        return None

    def read_code(self) -> str:
        return self._storage.read_code()

    # region Properties
    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def code_id(self) -> str:
        key = f"{self._prop_prefix}codename"
        if key not in self._props:
            self._set_code_id()
        return self._props.get(key)

    # endregion Properties
