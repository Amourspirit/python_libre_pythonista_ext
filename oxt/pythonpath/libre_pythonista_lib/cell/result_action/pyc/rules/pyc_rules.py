from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

from .rule_base import RuleBase
from .rule_empty import RuleEmpty
from .rule_error import RuleError
from .rule_float import RuleFloat
from .rule_int import RuleInt
from .rule_none import RuleNone
from .rule_pd_df import RulePdDf
from .rule_pd_df_headers import RulePdDfHeaders
from .rule_pd_ds import RulePdDs
from .rule_str import RuleStr
from .rule_tbl_data import RuleTblData
from .rule_mat_plot_figure import RuleMatPlotFigure
from .....utils.singleton_base import SingletonBase

if TYPE_CHECKING:
    from .pyc_rule_t import PycRuleT
    from .......___lo_pip___.config import Config
    from .......___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger import OxtLogger


class PycRules(SingletonBase):
    """Singleton Class. Manages rules for Versions"""

    # _instance = None

    # def __new__(cls) -> PycRules:
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._is_init = False
    #     return cls._instance

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
        self._default_rule = RuleNone
        self._log.debug(f"{self.__class__.__name__}.__init__() Initialized.")
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
        self._reg_rule(rule=RuleEmpty)
        self._reg_rule(rule=RulePdDfHeaders)
        self._reg_rule(rule=RulePdDf)
        self._reg_rule(rule=RulePdDs)
        self._reg_rule(rule=RuleFloat)
        self._reg_rule(rule=RuleInt)
        self._reg_rule(rule=RuleStr)
        self._reg_rule(rule=RuleTblData)
        self._reg_rule(rule=RuleMatPlotFigure)
        self._reg_rule(rule=RuleError)
        self._reg_rule(rule=RuleNone)

    def get_matched_rule(self, cell: CalcCell, data: DotDict) -> PycRuleT | None:
        """
        Get matched rules.

        The Data comes from the ``PySourceManager`` instance of ``PySource``.

        Args:
            cell (types.ModuleType): Calc Cell
            data (str): DotDict containing keys ``data``, ``py_src`` and maybe ``error``.

        Returns:
            List[PycRuleT]: Matched rule. Defaults to ``default_rule`` value.
        """
        is_db = self._log.is_debug
        if is_db:
            self._log.debug(f"get_matched_rule() cell: {cell.cell_obj}. Data Type {type(data).__name__}")
        result = None
        for rule in self._rules:
            inst = rule(cell, data)
            if inst.get_is_match():
                if is_db:
                    self._log.debug(f"get_matched_rule() Rule {inst} matched.")
                result = inst
                break
        if result is not None:
            return result
        if self._default_rule is not None:
            self._log.warning(f"get_matched_rule() No rule matched. Using default rule.")
            return self._default_rule(cell, data)
        # this should never happen LastDict is always a match
        self._log.warning(f"get_matched_rule() No rule matched.")
        return None

    def find_rule(self, cell: CalcCell) -> PycRuleT | None:
        """
        Find rule by name. ``default_rule`` is not used here.

        Args:
            cell (str): Calc Cell.

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

    # region Properties

    @property
    def default_rule(self) -> Type[PycRuleT] | None:
        """Gets/Sets the default rule type if no rules is matched."""
        return self._default_rule

    @default_rule.setter
    def default_rule(self, value: Type[PycRuleT] | None):
        self._default_rule = value

    # endregion Properties
