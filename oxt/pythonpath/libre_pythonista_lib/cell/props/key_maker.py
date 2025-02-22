from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.meta.singleton import Singleton
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_names import RuleNames
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.meta.singleton import Singleton
    from libre_pythonista_lib.cell.props.rule_names import RuleNames


class KeyMaker(metaclass=Singleton):
    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        self._cfg = BasicConfig()
        self._cell_cp_prefix = self._cfg.cell_cp_prefix
        self._rule_names = RuleNames()
        self._is_init = True

    # region Properties

    @property
    def cell_cp_prefix(self) -> str:
        """Gets the prefix for cell custom properties."""
        return self._cell_cp_prefix

    @property
    def ctl_state_key(self) -> str:
        """Gets the key for the control state."""
        return f"{self.cell_cp_prefix}ctl_state"

    @property
    def ctl_shape_key(self) -> str:
        """Gets the key for the control shape."""
        return f"{self.cell_cp_prefix}shape"

    @property
    def cell_addr_key(self) -> str:
        """Gets the address property."""
        return f"{self.cell_cp_prefix}addr"

    @property
    def cell_code_name(self) -> str:
        """Gets the key for the control shape."""
        return self._cfg.cell_cp_codename

    @property
    def ctl_orig_ctl_key(self) -> str:
        """Gets the key for the control original. This key is used to track when a cell control is to be replaced."""
        return f"{self.cell_cp_prefix}orig_ctl"

    @property
    def cell_array_ability_key(self) -> str:
        """Gets the key for the cell array ability. This key is used to determine if the cell can be converted to an array."""
        return f"{self.cell_cp_prefix}array_ability"

    @property
    def modify_trigger_event(self) -> str:
        """Gets the key for the modify trigger event."""
        return f"{self.cell_cp_prefix}modify_trigger_event"

    @property
    def pyc_rule_key(self) -> str:
        """Gets the key for the pyc rule."""
        return f"{self.cell_cp_prefix}pyc_rule"

    @property
    def rule_names(self) -> RuleNames:
        """Gets the rule names."""
        return self._rule_names

    # endregion Properties
