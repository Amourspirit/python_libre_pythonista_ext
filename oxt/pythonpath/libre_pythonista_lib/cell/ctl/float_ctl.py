from __future__ import annotations

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

from .simple_ctl import SimpleCtl


class FloatCtl(SimpleCtl):
    @override
    def get_rule_name(self) -> str:
        """Gets the rule name for this class instance."""
        return self.key_maker.rule_names.cell_data_type_float
