from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type
from ooodev.calc import CalcCell

from .rule_float import RuleFloat
from .rule_int import RuleInt
from .rule_str import RuleStr

if TYPE_CHECKING:
    from .pyc_rule_t import PycRuleT


class PycRules:
    """Singleton Class. Manages rules for Versions"""

    _instance = None

    def __new__(cls) -> PycRules:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_init = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize PycRules
        """
        if getattr(self, "_is_init", False):
            return
        self._rules: List[Type[PycRuleT]] = []
        self._register_known_rules()
        self._is_init = True

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule: Type[PycRuleT]) -> bool:
        return rule in self._rules

    # region Methods

    def get_index(self, rule: Type[PycRuleT]) -> int:
        """
        Get index of rule

        Args:
            rule (PycRuleT): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._rules.index(rule)

    def add_rule(self, rule: Type[PycRuleT]) -> None:
        """
        Register rule

        Args:
            rule (PycRuleT): Rule to register
        """
        if rule in self._rules:
            return
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[PycRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (PycRuleT): Rule to register
        """
        if rule in self._rules:
            return
        self._rules.insert(index, rule)

    def remove_rule(self, rule: Type[PycRuleT]):
        """
        Unregister Rule

        Args:
            rule (PycRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
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
        except IndexError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[PycRuleT]):
        self._rules.append(rule)

    def _register_known_rules(self):
        # re.compile(r"^(\w+)\s*=")
        self._reg_rule(rule=RuleFloat)
        self._reg_rule(rule=RuleInt)
        self._reg_rule(rule=RuleStr)

    def get_matched_rule(self, cell: CalcCell, data: Any) -> PycRuleT | None:
        """
        Get matched rules

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.

        Returns:
            List[PycRuleT]: List of matched rules
        """

        for rule in self._rules:
            inst = rule(cell, data)
            if inst.get_is_match():
                return inst
        # this should never happen LastDict is always a match
        return None

    # endregion Methods
