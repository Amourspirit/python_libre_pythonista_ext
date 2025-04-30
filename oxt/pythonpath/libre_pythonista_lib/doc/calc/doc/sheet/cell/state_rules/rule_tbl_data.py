from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.rule_base import RuleBase
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.state_rule_t import StateRuleT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.state_rules.rule_base import RuleBase
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.utils.custom_ext import override


class RuleTblData(RuleBase, StateRuleT):
    @override
    def _get_rule_kind(self) -> RuleNameKind:
        return RuleNameKind.CELL_DATA_TYPE_TBL_DATA

    @override
    def _get_is_match(self) -> bool:
        obj = self.data.get("data", None)
        if obj is None:
            return False
        if not isinstance(obj, (list, tuple)):
            return False

        for item in obj:
            if not isinstance(item, (list, tuple)):
                return False

        # # Optional: Check if all inner lists or tuples have the same length
        lengths = [len(item) for item in obj]
        return not (lengths and lengths.count(lengths[0]) != len(lengths))
