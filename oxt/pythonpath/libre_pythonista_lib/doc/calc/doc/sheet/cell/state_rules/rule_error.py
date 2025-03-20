from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cell.errors.general_error import GeneralError
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.rule_base import RuleBase
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.cell.errors.general_error import GeneralError
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.rule_base import RuleBase
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override


class RuleError(RuleBase, StateRuleT):
    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_error

    @override
    def _get_rule_kind(self) -> RuleNameKind:
        return RuleNameKind.CELL_DATA_TYPE_ERROR

    @override
    def _get_is_match(self) -> bool:
        result = self.data.get("data", None)
        return isinstance(result, GeneralError)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.cell.cell_obj}, ERROR)>"
