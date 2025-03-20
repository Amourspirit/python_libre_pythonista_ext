from __future__ import annotations
from typing import Any, TYPE_CHECKING
from abc import abstractmethod

from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from oxt.___lo_pip___.basic_config import BasicConfig
else:
    from libre_pythonista_lib.cell.props.key_maker import KeyMaker
    from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
    from ___lo_pip___.basic_config import BasicConfig


class RuleBase:
    def __init__(self, cell: CalcCell, data: DotDict[Any]) -> None:
        self._cell = cell
        self._dd_data = data
        self.cfg = BasicConfig()
        self.key_maker = KeyMaker()
        self.cell_pyc_rule_key = self.key_maker.pyc_rule_key
        self.__is_match = None

    @abstractmethod
    def _get_is_match(self) -> bool: ...

    @abstractmethod
    def _get_rule_kind(self) -> RuleNameKind: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.cell.cell_obj}, {self.data})>"

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def data(self) -> DotDict[Any]:
        return self._dd_data

    @data.setter
    def data(self, value: DotDict[Any]) -> None:
        self._dd_data = value

    @property
    def is_match(self) -> bool:
        """Gets if the rule is a match. Same as calling get_is_match()."""
        if self.__is_match is None:
            self.__is_match = self._get_is_match()
        return self.__is_match

    @property
    def rule_kind(self) -> RuleNameKind:
        """Gets the rule kind."""
        return self._get_rule_kind()
