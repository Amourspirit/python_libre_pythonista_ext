from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING


class FeatureKind(Enum):
    """
    Enum for the different kinds of actions a cell control can have.
    """

    ADD_CTL = "add_ctl"
    REMOVE_CTL = "remove_ctl"
    UPDATE_CTL = "update_ctl"
    UPDATE_CTL_ACTION = "update_ctl_action"
    GET_RULE_NAME = "get_rule_name"
    GET_CELL_POS_SIZE = "get_cell_pos_size"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_str(s: str) -> FeatureKind:
        """Converts a string to a FeatureKind."""
        for kind in FeatureKind:
            if kind.value == s:
                return kind
        return FeatureKind.UNKNOWN
