from __future__ import annotations
from typing import List, Type
from .progress_t import ProgressT
from .gnome_terminal import GnomeTerminal
from .win_terminal import WindowsTerminal
from .mac_terminal import MacTerminal
from .progress_dialog import ProgressDialog
from ...config import Config


class ProgressRules:
    """Manages rules for Versions"""

    def __init__(self, auto_register: bool = True) -> None:
        """
        Initialize VerRules

        Args:
            auto_register (bool, optional): Determines if know rules are automatically registered. Defaults to True.
        """
        self._rules: List[Type[ProgressT]] = []
        if auto_register:
            self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    # region Methods

    def register_rule(self, rule: Type[ProgressT]) -> None:
        """
        Register rule

        Args:
            rule (ProgressT): Rule to register
        """
        if rule in self._rules:
            # msg = f"{self.__class__.__name__}.register_rule() Rule is already registered"
            # log.logger.warning(msg)
            return
        self._reg_rule(rule=rule)

    def unregister_rule(self, rule: Type[ProgressT]):
        """
        Unregister Rule

        Args:
            rule (ProgressT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[ProgressT]):
        self._rules.append(rule)

    def _register_known_rules(self):
        cfg = Config()
        # ProgressDialog is registered first so it is the default and it is cross platform.
        # Depending on configuration, the other rules may apply.
        self.register_rule(rule=ProgressDialog)
        if cfg.is_win:
            self._reg_rule(rule=WindowsTerminal)
        elif cfg.is_linux:
            self._reg_rule(rule=GnomeTerminal)
        elif cfg.is_mac:
            self._reg_rule(rule=MacTerminal)

    def get_progress(self) -> ProgressT | None:
        """
        Get progress window if it is a match.

        Returns:
            ProgressT | None: Progress window if it is a match; Otherwise, None
        """

        for rule in self._rules:
            inst = rule()
            if inst.get_is_match():
                return inst
        return None

    # endregion Methods
