from __future__ import annotations
from enum import Enum


class CtlPropKind(Enum):
    """
    Enum for the different kinds of cell control properties.
    """

    CTL_STATE = "ctl_state"
    CTL_SHAPE = "shape"
    CELL_ADDR = "addr"
    CTL_ORIG = "orig_ctl"
    CELL_ARRAY_ABILITY = "array_ability"
    MODIFY_TRIGGER_EVENT = "modify_trigger_event"
    PYC_RULE = "pyc_rule"
