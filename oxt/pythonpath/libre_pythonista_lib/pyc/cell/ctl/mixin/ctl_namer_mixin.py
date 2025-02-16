from __future__ import annotations
from typing import Any, TYPE_CHECKING
import uno
from ooodev.calc import CalcCell
from .....ex import CustomPropertyMissingError
from .....log.log_mixin import LogMixin

if TYPE_CHECKING:
    from .......___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CtlNamerMixin:
    """Gets Control Names for Controls of a Given Cell"""

    def __init__(self, calc_cell: CalcCell) -> None:
        """
        Constructor

        Args:
            calc_cell (CalcCell): CalcCell object.

        Raises:
            CustomPropertyMissingError: Custom Property not found
        """
        self.__ctl_name = None
        self.__ctl_shape_name = None
        self.__calc_cell = calc_cell
        self.__code_name = ""
        self.__cfg = Config()
        self.__is_log = isinstance(self, LogMixin)

    def __ensure_code_name(self) -> None:
        if self.__code_name:
            return
        is_deleted_cell = self.__calc_cell.extra_data.get("deleted", False)

        if is_deleted_cell:
            self._code_name = self.__calc_cell.extra_data.code_name
        else:
            if self.__calc_cell.has_custom_property(self.__cfg.cell_cp_codename):
                self._code_name = self.__calc_cell.get_custom_property(self.__cfg.cell_cp_codename)
            else:
                if self.__is_log:
                    self.log.error("CtlNamer: __init__(): Custom Property not found: %s", self.__cfg.cell_cp_codename)  # type: ignore
                raise CustomPropertyMissingError(f"Custom Property not found: {self.__cfg.cell_cp_codename}")

    def __get_control_name(self) -> str:
        return f"{self.__cfg.general_code_name}_ctl_cell_{self._code_name}"

    def __get_ctl_shape_name(self) -> str:
        return f"SHAPE_{self.__get_control_name()}"

    @property
    def ctl_name(self) -> str:
        if self.__ctl_name is None:
            self.__ensure_code_name()
            self.__ctl_name = self.__get_control_name()
        return self.__ctl_name

    @property
    def ctl_shape_name(self) -> str:
        if self.__ctl_shape_name is None:
            self.__ensure_code_name()
            self.__ctl_shape_name = self.__get_ctl_shape_name()
        return self.__ctl_shape_name

    @property
    def code_name(self) -> str:
        self.__ensure_code_name()
        return self._code_name
