from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type
from ooodev.calc import CalcCell

from .rule_base import RuleBase
from .rule_float import RuleFloat
from .rule_int import RuleInt
from .rule_str import RuleStr
from .rule_pd_df import RulePdDf
from .rule_pd_ds import RulePdDs

if TYPE_CHECKING:
    from .pyc_rule_t import PycRuleT
    from .......___lo_pip___.config import Config
    from .......___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger import OxtLogger


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
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug(f"{self.__class__.__name__}.__init__() Initializing.")
        self._rules: List[Type[PycRuleT]] = []
        self._register_known_rules()
        self._is_init = True
        self._log.debug(f"{self.__class__.__name__}.__init__() Initialized.")

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
            self._log.debug(f"add_rule() Rule {rule} already registered.")
            return
        self._log.debug(f"add_rule() Rule {rule} registered.")
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[PycRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (PycRuleT): Rule to register
        """
        if rule in self._rules:
            self._log.debug(f"add_rule_at() Rule {rule} already registered.")
            return
        self._log.debug(f"add_rule_at() Rule {rule} registered at index {index}.")
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
            self._log.debug(f"remove_rule_at() Rule {rule} removed.")
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
            self._log.debug(f"remove_rule_at() Rule at index {index} removed.")
        except IndexError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            self._log.error(msg, exc_info=True)
            raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[PycRuleT]):
        self._rules.append(rule)

    def _register_known_rules(self):
        # re.compile(r"^(\w+)\s*=")
        self._reg_rule(rule=RulePdDf)
        self._reg_rule(rule=RulePdDs)
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
        is_db = self._log.is_debug
        if is_db:
            self._log.debug(f"get_matched_rule() cell: {cell.cell_obj}. Data Type {type(data).__name__}")
        for rule in self._rules:
            inst = rule(cell, data)
            if inst.get_is_match():
                if is_db:
                    self._log.debug(f"get_matched_rule() Rule {inst} matched.")
                return inst
        # this should never happen LastDict is always a match
        self._log.warning(f"get_matched_rule() No rule matched.")
        return None

    def find_rule(self, cell: CalcCell) -> PycRuleT | None:
        """
        Find rule by name

        Args:
            rule_name (str): Name of rule

        Returns:
            PycRuleT: Rule if found. The returned instance will have no data.
        """
        key = RuleBase.get_rule_name_key()
        if not cell.has_custom_property(key):
            return None
        rule_name = cell.get_custom_property(key)

        for rule in self._rules:
            inst = rule(cell, None)
            if inst.name == rule_name:
                self._log.debug(f"find_rule() Rule {inst} found.")
                return inst
        # this should never happen LastDict is always a match
        self._log.warning(f"find_rule() No rule found.")
        return None

    # endregion Methods
