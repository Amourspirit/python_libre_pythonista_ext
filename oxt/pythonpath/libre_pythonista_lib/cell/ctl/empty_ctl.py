from __future__ import annotations
from typing import Any

from .simple_ctl import SimpleCtl


class EmptyCtl(SimpleCtl):

    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_empty

    def add_ctl(self) -> Any:
        shape = super().add_ctl()
        return shape
