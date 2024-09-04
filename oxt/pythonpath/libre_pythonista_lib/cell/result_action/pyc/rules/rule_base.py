from __future__ import annotations
from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict
from ....props.key_maker import KeyMaker

if TYPE_CHECKING:
    from .......___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class RuleBase:
    def __init__(self, cell: CalcCell, data: DotDict) -> None:
        self._cell = cell
        self._dd_data = data
        self.cfg = Config()
        self.key_maker = KeyMaker()
        self.cell_prop_key = self.key_maker.modify_trigger_event
        self.cell_pyc_rule_key = self.key_maker.pyc_rule_key

    def get_is_match(self) -> bool:
        raise NotImplementedError

    def get_dispatch_state(self) -> str:
        """
        Gets the dispatch command the toggles the state such as ``.uno:libre_pythonista.calc.menu.code.df.state``.

        This is an empty string for rules that do not support state.
        """
        return ""

    def action(self) -> Any:
        return self.data

    def _update_properties(self, **kwargs: Any) -> None:
        dd = DotDict(**kwargs)
        self.cell.set_custom_properties(dd)

    def _get_data_type_name(self) -> str:
        raise NotImplementedError

    def _get_name(self) -> str:
        return self._get_data_type_name()

    def remove_custom_properties(self) -> None:
        """Removes the custom properties that were added for this rule"""
        if self._cell.has_custom_property(self.cell_prop_key):
            self.cell.remove_custom_property(self.cell_prop_key)
        if self._cell.has_custom_property(self.cell_pyc_rule_key):
            self.cell.remove_custom_property(self.cell_pyc_rule_key)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.cell.cell_obj}, {self.data})>"

    @property
    def is_match(self) -> bool:
        """Gets if the rule is a match. Same as calling get_is_match()."""
        return self.get_is_match()

    @property
    def data_type_name(self) -> str:
        """Gets the data type name."""
        return self._get_data_type_name()

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def name(self) -> str:
        """Gets the data type name."""
        return self._get_name()

    @property
    def data(self) -> DotDict:
        return self._dd_data

    @data.setter
    def data(self, value: DotDict) -> None:
        self._dd_data = value

    @staticmethod
    def get_rule_name_key() -> str:
        return KeyMaker().pyc_rule_key
