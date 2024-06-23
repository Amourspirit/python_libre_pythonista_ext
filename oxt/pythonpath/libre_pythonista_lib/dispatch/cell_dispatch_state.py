from __future__ import annotations
from ooodev.calc import CalcCell
from ..const import UNO_DISPATCH_CODE_EDIT, UNO_DISPATCH_DF_STATE, UNO_DISPATCH_DS_STATE, UNO_DISPATCH_DATA_TBL_STATE
from ..cell.props.key_maker import KeyMaker
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind


class CellDispatchState:
    """Class to get the dispatch state of a cell."""

    def __init__(self, cell: CalcCell):
        self._cell = cell
        self._ctl_state = CtlState(cell)
        self._cache = {}
        self._key_maker = KeyMaker()

    def is_dispatch_enabled(self, cmd: str) -> bool:
        global UNO_DISPATCH_CODE_EDIT
        if cmd == UNO_DISPATCH_CODE_EDIT:
            if not self.sheet_locked:
                return True
            return not self.cell_locked
        return True

    def get_rule_dispatch_cmd(self) -> str:
        """
        Gets the dispatch command that matches the current pyc rule.

        Returns:
            str: The dispatch command.
        """

        rules = self._key_maker.rule_names
        rule = self._cell.get_custom_property(self._key_maker.pyc_rule_key, "")
        if not rule:
            return ""
        if rule == rules.cell_data_type_pd_df:
            return UNO_DISPATCH_DF_STATE
        if rule == rules.cell_data_type_pd_series:
            return UNO_DISPATCH_DS_STATE
        if rule == rules.cell_data_type_tbl_data:
            return UNO_DISPATCH_DATA_TBL_STATE
        return ""

    def get_state(self) -> StateKind:
        """
        Gets the state

        Returns:
            StateKind: The state.
        """
        return self._ctl_state.get_state()

    def set_state(self, value: StateKind) -> None:
        """
        Sets the state

        Args:
            value (StateKind): The state.
        """
        self._ctl_state.set_state(value)

    # region Properties
    @property
    def sheet_locked(self) -> bool:
        key = "sheet_locked"
        if key not in self._cache:
            self._cache[key] = self._cell.calc_sheet.is_sheet_protected()
        return self._cache[key]

    @property
    def cell_locked(self) -> bool:
        key = "cell_locked"
        if key not in self._cache:
            self._cache[key] = self._cell.cell_protection.is_locked
        return self._cache[key]

    # endregion Properties