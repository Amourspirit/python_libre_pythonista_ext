from __future__ import annotations
from typing import Any
from ooodev.utils.color import StandardColor

from .simple_ctl import SimpleCtl


class ErrorCtl(SimpleCtl):

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_error

    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        return shape

    def _get_button_bg_color(self) -> int:
        return StandardColor.RED_LIGHT3
