from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcCell
from .simple_ctl import SimpleCtl
from .float_ctl import FloatCtl
from .str_ctl import StrCtl
from .data_frame_ctl import DataFrameCtl
from .data_series_ctl import DataSeriesCtl
from ...log.log_inst import LogInst
from ..props.key_maker import KeyMaker

if TYPE_CHECKING:
    from ..result_action.pyc.rules.pyc_rule_t import PycRuleT


class CtlMgr:
    def __init__(self):
        self._log = LogInst()
        self._key_maker = KeyMaker()

    def set_ctl_from_pyc_rule(self, rule: PycRuleT):
        """
        Event handler for when a cell custom property is modified.

        Args:
            event (EventArgs): Event data for when a cell custom property is modified.

        Note:
            ``event.event_data`` is a DotDict with the following keys:
            - absolute_name: str
            - event_obj: ``com.sun.star.lang.EventObject``
            - code_name: str
            - trigger_name: str
            - remove_custom_property: bool
            - calc_cell: CalcCell
            - cell_cp_codename: Unique code name for cell custom property
        """
        try:
            ctl = self._get_rule(rule.data_type_name, rule.cell)
            if ctl:
                ctl.add_ctl()
        except Exception:
            self._log.error("CtlMgr - set_ctl_from_pyc_rule() Error setting control for cell", exc_info=True)
            raise

    def _get_rule(self, rule_name: str, cell: CalcCell) -> SimpleCtl | None:
        rules = self._key_maker.rule_names
        if rule_name in (rules.cell_data_type_float, rules.cell_data_type_int):
            return FloatCtl(cell)
        if rule_name == rules.cell_data_type_str:
            return StrCtl(cell)
        if rule_name == rules.cell_data_type_pd_df:
            return DataFrameCtl(cell)
        if rule_name == rules.cell_data_type_pd_series:
            return DataSeriesCtl(cell)
        is_deleted = cell.extra_data.get("deleted", False)
        if is_deleted:
            self._log.debug(f"CtlMgr - _get_rule() Cell is deleted: {cell.cell_obj}. Returning SimpleCtl instance.")
            return SimpleCtl(cell)
        return None

    def update_ctl(self, cell: CalcCell) -> None:
        """Updates the Control for a cell if it exists."""
        km = self._key_maker
        try:
            self._log.debug(f"CtlMgr - update_ctl() Updating control for cell {cell.cell_obj}")

            key = km.pyc_rule_key
            is_deleted = cell.extra_data.get("deleted", False)
            if is_deleted:
                self._log.debug(f"CtlMgr - update_ctl() Cell is deleted: {cell.cell_obj}. Removing control.")
                self.remove_ctl(cell)
                return
            else:
                if not cell.has_custom_property(key):
                    self._log.debug(
                        f"CtlMgr - update_ctl() No custom property found for cell {cell.cell_obj}. Returning."
                    )
                    return
                rule_name = cell.get_custom_property(key)

            ctl = self._get_rule(rule_name, cell)
            if ctl:
                ctl.update_ctl()
                self._log.debug(f"CtlMgr - update_ctl() Updated control for cell {cell.cell_obj}")
            else:
                self._log.debug(f"CtlMgr - update_ctl() No control to update for cell {cell.cell_obj}")
        except Exception:
            self._log.error("CtlMgr - update_ctl() Error updating control for cell", exc_info=True)

    def remove_ctl(self, cell: CalcCell) -> None:
        """Removes the control for a cell if it exists."""
        km = self._key_maker
        try:
            self._log.debug(f"CtlMgr - remove_ctl() Removing control for cell {cell.cell_obj}")

            key = km.pyc_rule_key
            is_deleted = cell.extra_data.get("deleted", False)
            if is_deleted:
                rule_name = ""
            else:
                if not cell.has_custom_property(key):
                    self._log.debug(
                        f"CtlMgr - remove_ctl() No custom property found for cell {cell.cell_obj}. Returning."
                    )
                    return
                rule_name = cell.get_custom_property(key)

            ctl = self._get_rule(rule_name, cell)
            if ctl:
                ctl.remove_ctl()
                self._log.debug(f"CtlMgr - remove_ctl() Removed control for cell {cell.cell_obj}")
            else:
                self._log.debug(f"CtlMgr - remove_ctl() No control to remove for cell {cell.cell_obj}")
        except Exception:
            self._log.error("CtlMgr - remove_ctl() Error setting control for cell", exc_info=True)
