from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
else:
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind


class StateRuleT(Protocol):
    """
    A class to represent a cell formula state rule.
    """

    def __init__(self, cell: CalcCell, data: DotDict[Any]) -> None: ...

    @property
    def cell(self) -> CalcCell: ...

    @property
    def data(self) -> DotDict[Any]: ...

    @data.setter
    def data(self, value: DotDict[Any]) -> None: ...

    @property
    def is_match(self) -> bool:
        """Gets if the rule is a match. Same as calling get_is_match()."""
        ...

    @property
    def rule_kind(self) -> RuleNameKind:
        """Gets the rule kind."""
        ...
