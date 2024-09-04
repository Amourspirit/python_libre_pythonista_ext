from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type
import pandas as pd

if TYPE_CHECKING:
    from .pd_rules.pd_rule_t import PdRuleT


class PandasDfConverter:
    """Pandas Rules Class."""

    def __init__(self) -> None:
        """
        Initialize
        """
        if getattr(self, "_is_init", False):
            return
        self._rules: List[Type[PdRuleT]] = []
        self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule: Type[PdRuleT]) -> bool:
        return rule in self._rules

    # region Methods

    def get_index(self, rule: Type[PdRuleT]) -> int:
        """
        Get index of rule

        Args:
            rule (PdRuleT): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._rules.index(rule)

    def add_rule(self, rule: Type[PdRuleT]) -> None:
        """
        Register rule

        Args:
            rule (PdRuleT): Rule to register
        """
        if rule in self._rules:
            # self._log.debug(f"add_rule() Rule {rule} already registered.")
            return
        # self._log.debug(f"add_rule() Rule {rule} registered.")
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[PdRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (PdRuleT): Rule to register
        """
        if rule in self._rules:
            # self._log.debug(f"add_rule_at() Rule {rule} already registered.")
            return
        # self._log.debug(f"add_rule_at() Rule {rule} registered at index {index}.")
        self._rules.insert(index, rule)

    def remove_rule(self, rule: Type[PdRuleT]):
        """
        Unregister Rule

        Args:
            rule (PdRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
            # self._log.debug(f"remove_rule_at() Rule {rule} removed.")
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def remove_rule_at(self, index: int):
        """
        Unregister Rule at index

        Args:
            index (int): Index to remove rule

        Raises:
            ValueError: If an error occurs
        """
        try:
            del self._rules[index]
            # self._log.debug(f"remove_rule_at() Rule at index {index} removed.")
        except IndexError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            # self._log.error(msg, exc_info=True)
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[PdRuleT]):
        self._rules.append(rule)

    def _register_known_rules(self):
        return

    def apply_rules(self, value: pd.DataFrame) -> pd.DataFrame:
        """
        Applies all rules to the DataFrame.

        Args:
            value: DataFrame to apply rules to.

        Returns:
            pd.DataFrame: A Copy of the DataFrame with rules applied.
        """
        # is_db = self._log.is_debug
        # if is_db:
        #     self._log.debug(f"get_matched_rule() cell: {cell.cell_obj}. Data Type {type(data).__name__}")
        df = value.copy()
        for rule in self._rules:
            inst = rule()
            inst.convert(df)
        return df

    # endregion Methods
