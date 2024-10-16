from __future__ import annotations
from typing import Any

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

from .rule_base import RuleBase


class RuleNone(RuleBase):

    @override
    def get_is_match(self, value: Any) -> bool:
        return value is None

    @override
    def convert(self, value: Any) -> Any:
        return ""
