"""
Class that manages cell code.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from ooodev.calc import CalcCell
from ooodev.utils import gen_util as gUtil
from ooodev.utils.helper.dot_dict import DotDict
from .cell_code_storage import CellCodeStorage

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


class PyCell:
    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._cfg = Config()
        self._props = self._get_properties()
        self._storage = CellCodeStorage(self)

    def _get_properties(self) -> DotDict:
        if self._cell.has_custom_properties():
            props = self._cell.get_custom_properties()
        else:
            props = DotDict()
        return props

    def _set_code_id(self) -> None:
        key = self._cfg.cell_cp_codename
        str_id = "id_" + gUtil.Util.generate_random_alpha_numeric(14)
        self._cell.set_custom_property(key, str_id)
        setattr(self._props, key, str_id)
        return None

    def has_code(self) -> bool:
        key = self._cfg.cell_cp_codename
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
        key = self._cfg.cell_cp_codename
        if key not in self._props:
            self._set_code_id()
        return self._props.get(key)

    # endregion Properties
