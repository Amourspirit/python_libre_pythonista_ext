from __future__ import annotations
from typing import Iterable, List, Type
from .carrot import Carrot
from .equals import Equals
from .equals_star import EqualsStar
from .greater import Greater
from .greater_equal import GreaterEqual
from .lesser import Lesser
from .lesser_equal import LesserEqual
from .not_equals import NotEquals
from .tilde import Tilde
from .tilde_eq import TildeEq
from .ver_proto import VerProto
from .wildcard import Wildcard

# https://www.darius.page/pipdev/


class VerRules:
    """Manages rules for Versions"""

    def __init__(self, auto_register: bool = True) -> None:
        """
        Initialize VerRules

        Args:
            auto_register (bool, optional): Determines if know rules are automatically registered. Defaults to True.
        """
        self._rules: List[Type[VerProto]] = []
        if auto_register:
            self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    # region Methods

    def register_rule(self, rule: Type[VerProto]) -> None:
        """
        Register rule

        Args:
            rule (VerProto): Rule to register
        """
        if rule in self._rules:
            # msg = f"{self.__class__.__name__}.register_rule() Rule is already registered"
            # log.logger.warning(msg)
            return
        self._reg_rule(rule=rule)

    def unregister_rule(self, rule: Type[VerProto]):
        """
        Unregister Rule

        Args:
            rule (VerProto): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[VerProto]):
        self._rules.append(rule)

    def _register_known_rules(self):
        self._reg_rule(rule=Carrot)
        self._reg_rule(rule=Equals)
        self._reg_rule(rule=EqualsStar)
        self._reg_rule(rule=Greater)
        self._reg_rule(rule=GreaterEqual)
        self._reg_rule(rule=Lesser)
        self._reg_rule(rule=LesserEqual)
        self._reg_rule(rule=NotEquals)
        self._reg_rule(rule=Tilde)
        self._reg_rule(rule=TildeEq)
        self._reg_rule(rule=Wildcard)

    def split_and_strip(self, string: str) -> List[str]:
        """Split a string by commas and strip any leading or lagging whitespace.

        Args:
            string (str): The input string.

        Returns:
            List[str]: The list of substrings with leading and lagging whitespace removed.
        """
        clean_str = string.replace(";", ",")
        return [s.strip() for s in clean_str.split(",")]

    def get_partial_matched_rules(self, vstr: str) -> List[VerProto]:
        """
        Get matched rules

        Args:
            vstr (str): Version in string form, e.g. ``==1.2.3``

        Returns:
            List[VerProto]: List of matched rules
        """
        results: List[VerProto] = []
        for rule in self._rules:
            inst = rule(vstr=vstr)
            if inst.get_is_match():
                results.append(inst)
        return results

    def get_matched_rules(self, vstr: str) -> List[VerProto]:
        """
        Get matched rules

        Args:
            vstr (str): Version in string form, e.g. ``==1.2.3`` or ``>=1.2.3,<2.0.0``

        Returns:
            List[VerProto]: List of matched rules
        """
        ver_strings = self.split_and_strip(vstr)

        results: List[VerProto] = []

        for ver_str in ver_strings:
            results.extend(self.get_partial_matched_rules(ver_str))
        return results

    def get_installed_is_valid(self, vstr: str, check_version: str) -> bool:
        """
        Gets if the installed version is valid when compared to this rule.

        Args:
            vstr (str): Version in string form, e.g. ``==1.2.3`` or ``>=1.2.3,<2.0.0``
            check_version (str): The installed version to check. Eg: ``1.2.3``

        Returns:
            bool: True if the installed version is valid, False otherwise.
        """
        rules = self.get_matched_rules(vstr)
        return self.get_installed_is_valid_by_rules(rules, check_version)

    def get_installed_is_valid_by_rules(self, rules: Iterable[VerProto], check_version: str) -> bool:
        """
        Gets if the installed version is valid when compared to this rule.

        Args:
            rules (Iterable[VerProto]): List of rules to check
            check_version (str): The installed version to check. Eg: ``1.2.3``

        Returns:
            bool: True if the installed version is valid, False otherwise.
        """
        if not rules:
            return False
        return all(rule.get_installed_is_valid(check_version) for rule in rules)

    # endregion Methods
