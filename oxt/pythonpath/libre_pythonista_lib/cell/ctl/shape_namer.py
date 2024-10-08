from __future__ import annotations
from typing import Any, TYPE_CHECKING
import uno
from ooodev.calc import CalcCell
from ...log.log_inst import LogInst
from ...ex import CustomPropertyMissingError

if TYPE_CHECKING:
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class ShapeNamer:
    """Gets Control Names for Controls of a Given Cell"""

    def __init__(self, calc_cell: CalcCell):
        """
        Constructor

        Args:
            calc_cell (CalcCell): CalcCell object.

        Raises:
            CustomPropertyMissingError: Custom Property not found
        """
        self._ctl_name = None
        self._shape_name = None
        self._cfg = Config()
        self.log = LogInst()
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)

        if self.is_deleted_cell:
            self._code_name = calc_cell.extra_data.code_name
        else:
            if calc_cell.has_custom_property(self._cfg.cell_cp_codename):
                self._code_name = calc_cell.get_custom_property(self._cfg.cell_cp_codename)
            else:
                with self.log.indent(True):
                    self.log.error(f"CtlNamer: __init__(): Custom Property not found: {self._cfg.cell_cp_codename}")
                raise CustomPropertyMissingError(f"Custom Property not found: {self._cfg.cell_cp_codename}")

    def _get_shape_name(self) -> str:
        return f"SHAPE_{self._cfg.general_code_name}_cell_{self._code_name}"

    @property
    def shape_name(self) -> str:
        if self._shape_name is None:
            self._shape_name = self._get_shape_name()
        return self._shape_name

    @property
    def code_name(self) -> str:
        return self._code_name
