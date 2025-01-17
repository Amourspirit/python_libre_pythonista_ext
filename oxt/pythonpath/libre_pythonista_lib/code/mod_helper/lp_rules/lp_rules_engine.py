from __future__ import annotations
from typing import List, Type, TYPE_CHECKING
from .rule_cell_only import RuleCellOnly
from .rule_empty import RuleEmpty
from .rule_named_range import RuleNamedRange
from .rule_range_only import RuleRangeOnly
from .rule_sheet_cell import RuleSheetCell
from .rule_sheet_named_range import RuleSheetNamedRange
from .rule_sheet_range import RuleSheetRange

if TYPE_CHECKING:
    from .lp_rule_t import LpRuleT


class LpRulesEngine:
    """Manages rules for Lp Function"""

    def __init__(self, auto_register: bool = True) -> None:
        """
        Initialize CodeRules

        Args:
            auto_register (bool, optional): Determines if know rules are automatically registered. Defaults to True.
        """
        self._rules: List[Type[LpRuleT]] = []
        if auto_register:
            self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule: Type[LpRuleT]) -> bool:
        return rule in self._rules

    # region Methods

    def get_index(self, rule: Type[LpRuleT]) -> int:
        """
        Get index of rule

        Args:
            rule (LpRuleT): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._rules.index(rule)

    def add_rule(self, rule: Type[LpRuleT]) -> None:
        """
        Register rule

        Args:
            rule (LpRuleT): Rule to register
        """
        if rule in self._rules:
            return
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[LpRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (LpRuleT): Rule to register
        """
        if rule in self._rules:
            return
        self._rules.insert(index, rule)

    def remove_rule(self, rule: Type[LpRuleT]) -> None:
        """
        Unregister Rule

        Args:
            rule (LpRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
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
        except IndexError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[LpRuleT]) -> None:
        self._rules.append(rule)

    def _register_known_rules(self) -> None:
        # order matters
        self._reg_rule(rule=RuleEmpty)
        self._reg_rule(rule=RuleRangeOnly)
        self._reg_rule(rule=RuleCellOnly)
        self._reg_rule(rule=RuleSheetRange)
        self._reg_rule(rule=RuleSheetCell)
        self._reg_rule(rule=RuleNamedRange)
        self._reg_rule(rule=RuleSheetNamedRange)

    def get_matched_rule(self, value: str) -> LpRuleT:
        """
        Get matched rules

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.

        Returns:
            List[LpRuleT]: List of matched rules
        """
        found_rule = None
        for rule in self._rules:
            inst = rule(value)

            if inst.get_is_match():
                found_rule = inst
                break
        if found_rule:
            return found_rule
        # this should never happen LastDict is always a match
        raise ValueError(f"No rule matched for: {value}")

    def __repr__(self) -> str:
        return f"<LpRulesEngine()>"

    # endregion Methods
