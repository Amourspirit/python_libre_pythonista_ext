from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type, Union


if TYPE_CHECKING:
    from .rules.array_rule_t import ArrayRuleT


class ArrayRules:
    """Array Rules Class."""

    def __init__(self) -> None:
        """
        Initialize
        """
        if getattr(self, "_is_init", False):
            return
        self._rules: List[Type[ArrayRuleT]] = []
        self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule: Type[ArrayRuleT]) -> bool:
        return rule in self._rules

    # region Methods

    def get_index(self, rule: Type[ArrayRuleT]) -> int:
        """
        Get index of rule

        Args:
            rule (ArrayRuleT): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._rules.index(rule)

    def add_rule(self, rule: Type[ArrayRuleT]) -> None:
        """
        Register rule

        Args:
            rule (ArrayRuleT): Rule to register
        """
        if rule in self._rules:
            # self._log.debug(f"add_rule() Rule {rule} already registered.")
            return
        # self._log.debug(f"add_rule() Rule {rule} registered.")
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[ArrayRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (ArrayRuleT): Rule to register
        """
        if rule in self._rules:
            # self._log.debug(f"add_rule_at() Rule {rule} already registered.")
            return
        # self._log.debug(f"add_rule_at() Rule {rule} registered at index {index}.")
        self._rules.insert(index, rule)

    def remove_rule(self, rule: Type[ArrayRuleT]) -> None:
        """
        Unregister Rule

        Args:
            rule (ArrayRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
            # self._log.debug(f"remove_rule_at() Rule {rule} removed.")
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def remove_rule_at(self, index: int) -> None:
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

    def _reg_rule(self, rule: Type[ArrayRuleT]) -> None:
        self._rules.append(rule)

    def _register_known_rules(self) -> None:
        return

    def get_matched_rule(self, value: Any) -> Union[ArrayRuleT, None]:  # noqa: ANN401
        """
        Get matched rules

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.

        Returns:
            List[ArrayRuleT]: Matched rule. Defaults to ``default_rule`` value.
        """
        # is_db = self._log.is_debug
        # if is_db:
        #     self._log.debug(f"get_matched_rule() cell: {cell.cell_obj}. Data Type {type(data).__name__}")
        result = None
        for rule in self._rules:
            inst = rule()
            if inst.get_is_match(value):
                # if is_db:
                #     self._log.debug(f"get_matched_rule() Rule {inst} matched.")
                result = inst
                break
        return result

    # endregion Methods
