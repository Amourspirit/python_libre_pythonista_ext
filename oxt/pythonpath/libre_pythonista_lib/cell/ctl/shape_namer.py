from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.ex.exceptions import CustomPropertyMissingError
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.ex.exceptions import CustomPropertyMissingError


class ShapeNamer(LogMixin):
    """Gets Control Names for Controls of a Given Cell"""

    def __init__(self, calc_cell: CalcCell) -> None:
        """
        Constructor

        Args:
            calc_cell (CalcCell): CalcCell object.

        Raises:
            CustomPropertyMissingError: Custom Property not found
        """
        LogMixin.__init__(self)
        self._ctl_name = None
        self._shape_name = None
        self._cfg = BasicConfig()
        self.is_deleted_cell = calc_cell.extra_data.get("deleted", False)

        if self.is_deleted_cell:
            self._code_name = calc_cell.extra_data.code_name
        else:
            if calc_cell.has_custom_property(self._cfg.cell_cp_codename):
                self._code_name = calc_cell.get_custom_property(self._cfg.cell_cp_codename)
            else:
                with self.log.indent(True):
                    self.log.error("CtlNamer: __init__(): Custom Property not found: %s", self._cfg.cell_cp_codename)
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
