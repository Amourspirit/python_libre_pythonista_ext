from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.pyc_rule_t import PycRuleT
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_base import RuleBase
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_empty import RuleEmpty
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_error import RuleError
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_float import RuleFloat
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_int import RuleInt
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_mat_plot_figure import RuleMatPlotFigure
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_none import RuleNone
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_df import RulePdDf
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_df_headers import RulePdDfHeaders
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_ds import RulePdDs
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_str import RuleStr
    from oxt.pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.rule_tbl_data import RuleTblData
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.singleton_base import SingletonBase
else:
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_base import RuleBase
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_empty import RuleEmpty
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_error import RuleError
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_float import RuleFloat
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_int import RuleInt
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_mat_plot_figure import RuleMatPlotFigure
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_none import RuleNone
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_df import RulePdDf
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_df_headers import RulePdDfHeaders
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_pd_ds import RulePdDs
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_str import RuleStr
    from libre_pythonista_lib.cell.result_action.pyc.rules.rule_tbl_data import RuleTblData
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.singleton_base import SingletonBase

    PycRuleT = Any


class PycRules(LogMixin, SingletonBase):
    """Singleton Class. Manages rules for Versions"""

    def __init__(self) -> None:
        """
        Initialize PycRules
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        with self.log.indent(True):
            self.log.debug("__init__() Initializing.")
        self._rules: List[Type[PycRuleT]] = []
        self._register_known_rules()
        self._default_rule = RuleNone
        with self.log.indent(True):
            self.log.debug("__init__() Initialized.")
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
        with self.log.indent(True):
            if rule in self._rules:
                self.log.debug("add_rule() Rule %s already registered.", rule)
                return
            self.log.debug("add_rule() Rule %s registered.", rule)
            self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: Type[PycRuleT]) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (PycRuleT): Rule to register
        """
        with self.log.indent(True):
            if rule in self._rules:
                self.log.debug("add_rule_at() Rule %s already registered.", rule)
                return
            self.log.debug("add_rule_at() Rule %s registered at index %i.", rule, index)
            self._rules.insert(index, rule)

    def remove_rule(self, rule: Type[PycRuleT]) -> None:
        """
        Unregister Rule

        Args:
            rule (PycRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        with self.log.indent(True):
            try:
                self._rules.remove(rule)
                self.log.debug("remove_rule_at() Rule %s removed.", rule)
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
        with self.log.indent(True):
            try:
                del self._rules[index]
                self.log.debug("remove_rule_at() Rule at index %i removed.", index)
            except IndexError as e:
                msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
                self.log.error(msg, exc_info=True)
                raise ValueError(msg) from e

    def _reg_rule(self, rule: Type[PycRuleT]) -> None:
        self._rules.append(rule)

    def _register_known_rules(self) -> None:
        # re.compile(r"^(\w+)\s*=")
        self._reg_rule(rule=RuleEmpty)
        self._reg_rule(rule=RulePdDfHeaders)
        self._reg_rule(rule=RulePdDf)
        self._reg_rule(rule=RulePdDs)
        self._reg_rule(rule=RuleMatPlotFigure)
        self._reg_rule(rule=RuleInt)
        self._reg_rule(rule=RuleFloat)
        self._reg_rule(rule=RuleStr)
        self._reg_rule(rule=RuleTblData)
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
        with self.log.indent(True):
            is_db = self.log.is_debug
            if is_db:
                self.log.debug("get_matched_rule() cell: %s. Data Type %s", cell.cell_obj, type(data).__name__)
            result = None
            for rule in self._rules:
                inst = rule(cell, data)
                if inst.get_is_match():
                    if is_db:
                        self.log.debug("get_matched_rule() Rule %s matched.", inst)
                    result = inst
                    break
            if result is not None:
                return result
            if self._default_rule is not None:
                self.log.warning("get_matched_rule() No rule matched. Using default rule.")
                return self._default_rule(cell, data)
            # this should never happen LastDict is always a match
            self.log.warning("get_matched_rule() No rule matched.")
            return None

    def find_rule(self, cell: CalcCell) -> PycRuleT | None:
        """
        Find rule by name. ``default_rule`` is not used here.

        Args:
            cell (str): Calc Cell.

        Returns:
            PycRuleT: Rule if found. The returned instance will have no data.
        """
        with self.log.indent(True):
            key = RuleBase.get_rule_name_key()
            if not cell.has_custom_property(key):
                return None
            rule_name = cell.get_custom_property(key)

            for rule in self._rules:
                inst = rule(cell, None)
                if inst.name == rule_name:
                    self.log.debug("find_rule() Rule %s found.", inst)
                    return inst
            # this should never happen LastDict is always a match
            self.log.warning("find_rule() No rule found.")
            return None

    # endregion Methods

    # region Properties

    @property
    def default_rule(self) -> Type[PycRuleT] | None:
        """Gets/Sets the default rule type if no rules is matched."""
        return self._default_rule

    @default_rule.setter
    def default_rule(self, value: Type[PycRuleT] | None) -> None:
        self._default_rule = value

    # endregion Properties
