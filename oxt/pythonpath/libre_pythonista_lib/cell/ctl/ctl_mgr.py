from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type
from ooodev.calc import CalcCell
from .simple_ctl import SimpleCtl
from .float_ctl import FloatCtl
from .str_ctl import StrCtl
from .none_ctl import NoneCtl
from .empty_ctl import EmptyCtl
from .error_ctl import ErrorCtl
from .data_frame_ctl import DataFrameCtl
from .data_series_ctl import DataSeriesCtl
from .data_tbl_ctl import DataTblCtl
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
            ctl_type = self._get_rule(rule.data_type_name, rule.cell)
            if ctl_type:
                ctl = ctl_type(rule.cell)
                ctl.add_ctl()
        except Exception:
            self._log.error("CtlMgr - set_ctl_from_pyc_rule() Error setting control for cell", exc_info=True)
            raise

    def _get_rule(self, rule_name: str, cell: CalcCell) -> Type[SimpleCtl] | None:
        rules = self._key_maker.rule_names
        if rule_name in (rules.cell_data_type_float, rules.cell_data_type_int):
            return FloatCtl
        if rule_name == rules.cell_data_type_str:
            return StrCtl
        if rule_name == rules.cell_data_type_pd_df:
            return DataFrameCtl
        if rule_name == rules.cell_data_type_pd_series:
            return DataSeriesCtl
        if rule_name == rules.cell_data_type_error:
            return ErrorCtl
        if rule_name == rules.cell_data_type_none:
            return NoneCtl
        if rule_name == rules.cell_data_type_empty:
            return EmptyCtl
        if rule_name == rules.cell_data_type_tbl_data:
            return DataTblCtl
        is_deleted = cell.extra_data.get("deleted", False)
        if is_deleted:
            self._log.debug(f"CtlMgr - _get_rule() Cell is deleted: {cell.cell_obj}. Returning SimpleCtl instance.")
            return SimpleCtl
        return None

    def get_current_ctl_type_from_cell(self, cell: CalcCell) -> Type[SimpleCtl] | None:
        """Gets the control type for a cell."""
        with self._log.indent(True):
            km = self._key_maker
            try:
                self._log.debug(
                    f"CtlMgr - get_current_ctl_type_from_cell() Getting control type for cell {cell.cell_obj}"
                )

                key = km.pyc_rule_key
                is_deleted = cell.extra_data.get("deleted", False)
                if is_deleted:
                    self._log.debug(
                        f"CtlMgr - get_current_ctl_type_from_cell() Cell is deleted: {cell.cell_obj}. Returning None."
                    )
                    return None
                else:
                    if not cell.has_custom_property(key):
                        self._log.debug(
                            f"CtlMgr - get_current_ctl_type_from_cell() No custom property found for cell {cell.cell_obj}. Returning None."
                        )
                        return None
                    rule_name = cell.get_custom_property(key)

                ctl_type = self._get_rule(rule_name, cell)
                if ctl_type:
                    self._log.debug(
                        f"CtlMgr - get_current_ctl_type_from_cell() Found control type for cell {cell.cell_obj}"
                    )
                else:
                    self._log.debug(
                        f"CtlMgr - get_current_ctl_type_from_cell() No control type found for cell {cell.cell_obj}"
                    )
                return ctl_type
            except Exception:
                self._log.error(
                    "CtlMgr - get_current_ctl_type_from_cell() Error getting control type for cell", exc_info=True
                )
        return None

    def get_orig_ctl_type_from_cell(self, cell: CalcCell) -> Type[SimpleCtl] | None:
        """Gets the control type for a cell."""
        with self._log.indent(True):
            km = self._key_maker
            try:
                self._log.debug(
                    f"CtlMgr - get_orig_ctl_type_from_cell() Getting control type for cell {cell.cell_obj}"
                )

                key = km.ctl_orig_ctl_key
                is_deleted = cell.extra_data.get("deleted", False)
                if is_deleted:
                    self._log.debug(
                        f"CtlMgr - get_orig_ctl_type_from_cell() Cell is deleted: {cell.cell_obj}. Returning None."
                    )
                    return None
                else:
                    if not cell.has_custom_property(key):
                        self._log.debug(
                            f"CtlMgr - get_orig_ctl_type_from_cell() No custom property found for cell {cell.cell_obj}. Returning None."
                        )
                        return None
                    rule_name = cell.get_custom_property(key)

                ctl_type = self._get_rule(rule_name, cell)
                if ctl_type:
                    self._log.debug(
                        f"CtlMgr - get_orig_ctl_type_from_cell() Found control type for cell {cell.cell_obj}"
                    )
                else:
                    self._log.debug(
                        f"CtlMgr - get_orig_ctl_type_from_cell() No control type found for cell {cell.cell_obj}"
                    )
                return ctl_type
            except Exception:
                self._log.error(
                    "CtlMgr - get_orig_ctl_type_from_cell() Error getting control type for cell", exc_info=True
                )
        return None

    def update_ctl(self, cell: CalcCell) -> None:
        """Updates the Control for a cell if it exists."""
        # if the current control and original control are the same then just update the control.
        # if the current control and the original control are different then remove the original control and add the current control.
        # if the current control is None and the original control is not None then remove the original control.
        # if the current control is None and the original control is None then do nothing.
        # if current_ctl_type is not present then the cell has been modified and the original control need to be removed if it exist.
        with self._log.indent(True):
            current_ctl_type = self.get_current_ctl_type_from_cell(cell)
            # orig_ctl_type will always be present unless this a new cell.
            orig_ctl_type = self.get_orig_ctl_type_from_cell(cell)
            if current_ctl_type is None and orig_ctl_type is None:
                self._log.debug(f"CtlMgr - update_ctl() No control type found for cell {cell.cell_obj}. Returning.")
                return

            if orig_ctl_type is not None and current_ctl_type is not None and orig_ctl_type == current_ctl_type:
                self._log.debug(
                    f"CtlMgr - update_ctl() Control type for cell {cell.cell_obj} has not changed. Updating."
                )
                ctl = current_ctl_type(cell)
                ctl.update_ctl()  # refresh size and pos
                self._log.debug("CtlMgr - update_ctl() Done.")
                return

            if current_ctl_type is not None:
                # if there is no original then this is a new cell that the control has not been added to yet.
                if orig_ctl_type is None:
                    self._log.debug(
                        f"CtlMgr - update_ctl() Control type for cell {cell.cell_obj} has changed. Adding new control."
                    )
                    ctl = current_ctl_type(cell)
                    ctl.add_ctl()
                    self._log.debug("CtlMgr - update_ctl() Done.")
                    return
                # both controls exist and they are different
                self._log.debug(
                    f"CtlMgr - update_ctl() Control type for cell {cell.cell_obj} has changed. Removing old control."
                )
                old_ctl = orig_ctl_type(cell)
                old_ctl.remove_ctl()
                self._log.debug(f"CtlMgr - update_ctl() Removed Old Control. Adding new control.")
                ctl = current_ctl_type(cell)
                ctl.add_ctl()
                self._log.debug("CtlMgr - update_ctl() Done.")
                return
            else:
                if orig_ctl_type is not None:
                    self._log.debug(
                        f"CtlMgr - update_ctl() Control type for cell {cell.cell_obj} has been removed. Removing old control."
                    )
                    ctl = orig_ctl_type(cell)
                    ctl.remove_ctl()
            self._log.debug("CtlMgr - update_ctl() Done.")
        return

    def remove_ctl(self, cell: CalcCell) -> None:
        """Removes the control for a cell if it exists."""
        km = self._key_maker
        with self._log.indent(True):
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

                ctl_type = self._get_rule(rule_name, cell)
                if ctl_type:
                    ctl = ctl_type(cell)
                    ctl.remove_ctl()
                    self._log.debug(f"CtlMgr - remove_ctl() Removed control for cell {cell.cell_obj}")
                else:
                    self._log.debug(f"CtlMgr - remove_ctl() No control to remove for cell {cell.cell_obj}")
            except Exception:
                self._log.error("CtlMgr - remove_ctl() Error setting control for cell", exc_info=True)
