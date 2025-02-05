"""
Manages the code cells.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from contextlib import contextmanager
import threading
from ooodev.calc import CalcDoc, CalcCell, CalcSheet
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from .listen.code_cell_listener import CodeCellListener
from .listen.code_cell_listeners import CodeCellListeners
from .state.state_kind import StateKind
from ..code.cell_cache import CellCache
from ..code.py_source_mgr import PyInstance, PySourceManager
from ..code.py_source_mgr import PySource
from ..cell.ctl.ctl_mgr import CtlMgr
from ..cell.cell_info import CellInfo
from ..cell.props.key_maker import KeyMaker
from ..event.shared_event import SharedEvent
from .lpl_cell import LplCell
from ..style.default_style import DefaultStyle
from ..utils.singleton_base import SingletonBase
from ..sheet.sheet_mgr import SheetMgr
from ..dispatch.cell_dispatch_state import CellDispatchState
from ..const import DISPATCH_DF_STATE, UNO_DISPATCH_PY_OBJ_STATE
from ..const.event_const import (
    SHEET_MODIFIED,
    CALC_FORMULAS_CALCULATED,
    PYC_FORMULA_INSERTED,
    PYC_RULE_MATCH_DONE,
)
from ..log.log_inst import LogInst

from .array.array_mgr import ArrayMgr

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
    from ....___lo_pip___.debug.break_mgr import BreakMgr, check_breakpoint
    from .result_action.pyc.rules.pyc_rule_t import PycRuleT

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    from ___lo_pip___.debug.break_mgr import BreakMgr, check_breakpoint

    break_mgr = BreakMgr()
    # break_mgr.add_breakpoint("update_array_cells")


class CellMgr(SingletonBase):
    # _instances: Dict[str, CellMgr] = {}

    # def __new__(cls, doc: CalcDoc):
    #     key = f"doc_{doc.runtime_uid}"
    #     if not key in cls._instances:
    #         cls._instances[key] = super(CellMgr, cls).__new__(cls)
    #         cls._instances[key]._is_init = False
    #     return cls._instances[key]

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_is_init", False):
            return
        self._cfg = Config()
        self._doc = doc
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug(f"init for doc: {doc.runtime_uid}")
        self._is_db = self._log.is_debug
        self._listeners = CodeCellListeners()  # will automatically add listeners to all cells
        self._cell_cache = CellCache(doc)  # singleton
        self._py_inst = None  # PyInstance(doc)  # singleton
        self._ctl_mgr = CtlMgr()
        self._key_maker = KeyMaker()
        self._style = DefaultStyle()
        self._sheet_mgr = SheetMgr(self._doc)
        self._init_events()
        self._se = SharedEvent(doc)
        self._se.trigger_event("CellMgrCreated", EventArgs(self))
        self._subscribe_to_shared_events()
        self._cell_cache.subscribe_cell_addr_prop_update(self._fn_on_cell_cache_update_sheet_cell_addr_prop)
        self._se.subscribe_event(SHEET_MODIFIED, self._fn_on_sheet_modified)
        self._se.subscribe_event(CALC_FORMULAS_CALCULATED, self._fn_on_calc_formulas_calculated)
        self._se.subscribe_event(PYC_FORMULA_INSERTED, self._fn_on_calc_pyc_formula_inserted)
        self._se.subscribe_event(PYC_RULE_MATCH_DONE, self._fn_on_pyc_rule_matched)
        self.add_all_listeners()

        # self.remove_all_listeners()
        # self.add_all_listeners()

        self._is_init = True

    def dispose(self) -> None:
        if self._se is not None:
            self._se.trigger_event("CellMgrDisposed", EventArgs(self))

    # region Events Cell Cache
    def _on_cell_cache_update_sheet_cell_addr_prop(self, src: Any, event: EventArgs) -> None:
        """
        When the CellCache updates the cell's sheet address property this event is fired.

        When this event is fired the code listener for the cell gets is Absolute Name updated.
        """
        with self._log.noindent():
            is_db = self._log.is_debug
            if is_db:
                self._log.debug("_on_cell_cache_update_sheet_cell_addr_prop() Entering.")
            icp = event.event_data.icp
            code_name = cast(str, icp.code_name)
            if code_name in self._listeners:
                if is_db:
                    self._log.debug(f"Listener exists for code name: {code_name}")
                calc_cell = cast(CalcCell, event.event_data.calc_cell)
                listener = self._listeners[code_name]
                listener.update_absolute_name(name=calc_cell.component.AbsoluteName, cell_obj=calc_cell.cell_obj)
            else:
                if is_db:
                    self._log.debug("Listener does not exist for code name: %s", code_name)
            if is_db:
                self._log.debug("_on_cell_cache_update_sheet_cell_addr_prop() Done.")

    # endregion Events Cell Cache

    # region Events Sheet
    def _on_sheet_modified(self, src: Any, event: EventArgs) -> None:
        with self._log.noindent():
            self._log.debug("_on_sheet_modified() Entering.")
            # self.reset_py_inst()
            self._log.debug("_on_sheet_modified() Done.")

    def _on_calc_formulas_calculated(self, src: Any, event: EventArgs) -> None:
        with self._log.noindent():
            self._log.debug("_on_calc_formulas_calculated() Entering.")
            self.reset_py_inst(update_display=True)
            self._log.debug("_on_calc_formulas_calculated() Done.")

    def _on_calc_pyc_formula_inserted(self, src: Any, event: EventArgs) -> None:
        pass
        # SheetMgr subscribes to this event and ensures that the sheet calculate event is set.

        # with self._log.noindent():
        #     self._log.debug(f"_on_calc_pyc_formula_inserted() Entering.")
        #     self._sheet_mgr.ensure_sheet_calculate_event()
        #     self._log.debug(f"_on_calc_pyc_formula_inserted() Done.")

    # endregion Events Sheet

    # region PYC Events
    def _on_pyc_rule_matched(self, src: Any, event: EventArgs) -> None:
        # this event is raised in PY.C when a rule is matched.
        # So, basically every call to PY.C will raise this event.
        try:
            self._log.debug("_on_pyc_rule_matched() Entering.")
            dd = cast(DotDict, event.event_data)
            if self._log.is_debug:
                self._log.debug("Is First Cell: %s", dd.is_first_cell)
                self._log.debug("Is Last Cell: %s", dd.is_last_cell)

            if dd.is_last_cell:
                # it is imperative that the update be called in a new thread.
                # If not called in a new thread then chances are LibreOffice will totally crash.
                # Most likely the crash is because a re-calculation of the sheet is taking place,
                # and the update that can change the sheet cell formulas is being called at the same time.
                # By calling in a thread the crash is avoided and the sheet is updated without any issues.
                t = threading.Thread(target=update_array_cells, args=(self._doc,), daemon=True)
                t.start()

        except Exception:
            self._log.exception("_on_pyc_rule_matched()")
            raise

        self._log.debug("_on_pyc_rule_matched() Done")

    # endregion PYC Events

    # region Control Update Methods
    def _update_lp_cell_control(self, cell: CalcCell) -> None:
        """
        Update the control for a cell when the cell is modified.
        This may mean the the control get changed or removed.

        Args:
            cell (CalcCell): cell object.
        """
        with self._log.indent(True):
            self._log.debug(f"_update_py_event_control() Updating control for cell: {cell.cell_obj}")
            lpl = LplCell(cell)
            current_state = lpl.ctl_state
            if current_state != StateKind.PY_OBJ:
                self._log.debug(f"Current State: {current_state}. Setting to PY_OBJ")
                lpl.ctl_state = StateKind.PY_OBJ
            lpl.update_control()
            if current_state != StateKind.PY_OBJ:
                self._log.debug(f"Setting State back to: {current_state}")
                lpl.ctl_state = current_state
            self._log.debug("_update_py_event_control() Done.")

    def _update_controls_forward(self, cell: CalcCell) -> None:
        """
        Update the controls for this cell and cells that come after the current cell.

        Args:
            cell (CalcCell): cell object.
        """
        with self._log.indent(True):
            self._log.debug(f"_update_controls_forward() Updating controls for cells on and after: {cell.cell_obj}")
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            try:
                idx = self._cell_cache.get_cell_count(cell.cell_obj.sheet_idx)
                # count = self._cell_cache.get_cell_complete_count()
                count = self._cell_cache.get_cell_count(cell.cell_obj.sheet_idx)
                self._log.debug(f"Index: {idx} Count: {count}")
                cells = [cell]
                idx += 1
                for i in range(idx, count):
                    co = self._cell_cache.get_by_index(i)
                    cells.append(cell.calc_sheet[co])
                if cells and self._log.is_debug:
                    self._log.debug(f"Updating controls for {len(cells)} cells")
                    for current_cell in cells:
                        self._log.debug(f"Going to update control for cell: {current_cell.cell_obj}")
                for current_cell in cells:
                    self._update_lp_cell_control(current_cell)
            except Exception:
                self._log.error(
                    f"_update_controls_forward() Error updating controls for cell: {cell.cell_obj}",
                    exc_info=True,
                )

            self._log.debug("_update_controls_forward() Done.")

    def _update_py_event_formula(self, cell: CalcCell) -> None:
        # when code is updated the formula will be the same but the state may change.
        # This means if the state is being displayed as a formula array then it is possible
        # that the code changes not longer result in an array or data.
        # Also it is possible that the new code result has a different size of array.
        # If the current view state is Py_Obj then this is not an issue.
        # perhaps the best thing to do is to convert to single formula and display as py object only.
        # This is because the formula array is not a good representation of the data when it changes.

        # Get the current state of the cell.
        pass

    # endregion Control Update Methods

    # region Py Instance Events

    def on_py_code_updated(self, src: Any, event: EventArgs) -> None:
        # update controls for the affected cell
        # No need to handle the control update here.
        # DotDict(source=self, sheet_idx=sheet_idx, row=row, col=col, code=code, doc=self._doc)
        with self._log.indent(True):
            self._log.debug("on_py_code_updated() Entering.")
            cell_obj = CellObj.from_idx(
                col_idx=event.event_data.col,
                row_idx=event.event_data.row,
                sheet_idx=event.event_data.sheet_idx,
            )
            sheet = self._doc.sheets[event.event_data.sheet_idx]
            cell = sheet[cell_obj]
            self._update_controls_forward(cell)
            self._log.debug("on_py_code_updated() Done.")

    # endregion Py Instance Events

    # region Cell Events
    def _init_events(self) -> None:
        self._fn_on_cell_deleted = self.on_cell_deleted
        self._fn_on_cell_moved = self.on_cell_moved
        self._fn_on_cell_pyc_formula_removed = self.on_cell_pyc_formula_removed
        self._fn_on_cell_modified = self.on_cell_modified
        self._fn_on_cell_custom_prop_modify = self.on_cell_custom_prop_modify
        # region py instance events

        self._fn_on_py_code_updated = self.on_py_code_updated
        # endregion py instance events
        # region shared events
        self._fn_on_shared_dispatch_data_frame_state_before = self.on_shared_dispatch_data_frame_state_before
        self._fn_on_shared_dispatch_data_frame_state_after = self.on_shared_dispatch_data_frame_state_after

        self._fn_on_shared_dispatch_added_cell_formula = self.on_shared_dispatch_added_cell_formula
        self._fn_on_shared_dispatch_removed_cell_formula = self.on_shared_dispatch_removed_cell_formula
        self._fn_on_shared_dispatch_dispatch_add_array_formula = self.on_shared_dispatch_dispatch_add_array_formula
        self._fn_on_shared_dispatch_dispatch_remove_array_formula = (
            self.on_shared_dispatch_dispatch_remove_array_formula
        )
        # endregion shared events
        # region Cell Cache Events
        self._fn_on_cell_cache_update_sheet_cell_addr_prop = self._on_cell_cache_update_sheet_cell_addr_prop
        # endregion Cell Cache Events
        # region Sheet Events
        self._fn_on_sheet_modified = self._on_sheet_modified
        self._fn_on_calc_formulas_calculated = self._on_calc_formulas_calculated
        self._fn_on_calc_pyc_formula_inserted = self._on_calc_pyc_formula_inserted
        self._fn_py_inst_after_source_update = self._py_inst_after_source_update
        # endregion Sheet Events
        # region PYC Events
        self._fn_on_pyc_rule_matched = self._on_pyc_rule_matched
        # endregion PYC Events

    def on_cell_deleted(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is deleted.

        ``CalcCell.extra_data`` of event_data will the same key value pairs of the event_data keys.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following

        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: True
        - cell_info: CellInfo


        """
        with self._log.indent(True):
            dd = cast(DotDict, event.event_data)
            self._log.debug("on_cell_deleted() Entering.")
            self._remove_cell(calc_cell=dd.calc_cell)
            # self._remove_listener_from_cell(dd.event_obj.Source, dd.code_name)
            self._log.debug(f"Cell deleted: {dd.absolute_name}")

    def on_cell_moved(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is moved.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: current cell absolute name.
        - old_name: old cell absolute name.
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - cell_info: CellInfo
        - calc_cell: CalcCell
        - deleted: False

        """
        with self._log.indent(True):
            dd = cast(DotDict, event.event_data)
            self.reset_cell_cache()
            calc_cell = cast(CalcCell, dd.calc_cell)
            co = calc_cell.cell_obj
            addr = f"sheet_index={co.sheet_idx}&cell_addr={co}"
            calc_cell.set_custom_property(self._key_maker.cell_addr_key, addr)
            if self._log.is_debug:
                self._log.debug(f"Cell moved: {dd.absolute_name}")
                self._log.debug(f"Update Custom Prop: {self._key_maker.cell_addr_key} to {addr}")

    def on_cell_pyc_formula_removed(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell has pyc formula removed.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following:

        - absolute_name: current cell absolute name.
        - old_name: old cell absolute name.
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: False

        """
        with self._log.indent(True):
            dd = DotDict(absolute_name="UNKNOWN")
            try:
                self._log.debug("on_cell_pyc_formula_removed() Entering.")
                dd = cast(DotDict, event.event_data)
                self._remove_cell(calc_cell=dd.calc_cell)
                self._log.debug(f"on_cell_pyc_formula_removed() Leaving: {dd.absolute_name}")
            except Exception:
                self._log.error(
                    f"Error removing pyc formula from cell: {dd.absolute_name}",
                    exc_info=True,
                )

    def on_cell_modified(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is modified.

        ``CalcCell.extra_data`` of event_data will the same key value pairs of the event_data keys.

        ``EventArgs.event_data`` and ``EventArgs.event_data.calc_cell.extra_data`` will have the following:

        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - calc_cell: CalcCell
        - deleted: False
        - cell_info: CellInfo

        """
        with self._log.indent(True):
            dd = cast(DotDict, event.event_data)
            try:
                cell = cast("SheetCell", dd.event_obj.Source)
                ci = CellInfo(cell)

                if not ci.is_pyc_formula():
                    self._log.debug(
                        f"Formula has been modified or removed. Not a LibrePythonista cell: {dd.absolute_name}"
                    )
                    # address = cell.getCellAddress()
                    self._remove_cell(calc_cell=dd.calc_cell)
                is_first_cell = getattr(dd, "is_first_cell", False)
                is_last_cell = getattr(dd, "is_last_cell", False)
                self._log.debug(f"Is First Cell: {is_first_cell}")
                self._log.debug(f"Is Last Cell: {is_last_cell}")
            except Exception:
                self._log.error(f"Error modifying cell: {dd.absolute_name}", exc_info=True)

        self._log.debug(f"Cell modified: {dd.absolute_name}")

    def on_cell_custom_prop_modify(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell custom property is modified.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str
        - trigger_name: str
        - remove_custom_property: bool
        - calc_cell: CalcCell
        """
        return
        # try:
        #     if self._log.is_debug:
        #         self._log.debug(
        #             f"Cell custom property modify Event for {event.event_data.absolute_name} with event {event.event_data.trigger_name}"
        #         )
        #     ct_mgr = CtlMgr()
        #     ct_mgr.set_ctl(event)
        # except Exception:
        #     self._log.error("Error setting custom property control", exc_info=True)

    # endregion Cell Events

    # region Shared Events
    def _subscribe_to_shared_events(self) -> None:
        self._se.subscribe_event(
            f"{DISPATCH_DF_STATE}_before_dispatch",
            self._fn_on_shared_dispatch_data_frame_state_before,
        )
        self._se.subscribe_event(
            f"{DISPATCH_DF_STATE}_after_dispatch",
            self._fn_on_shared_dispatch_data_frame_state_after,
        )

        self._se.subscribe_event(
            "dispatch_added_cell_formula",
            self._fn_on_shared_dispatch_added_cell_formula,
        )
        self._se.subscribe_event(
            "dispatch_removed_cell_formula",
            self._fn_on_shared_dispatch_removed_cell_formula,
        )
        self._se.subscribe_event(
            "dispatch_add_array_formula",
            self._fn_on_shared_dispatch_dispatch_add_array_formula,
        )
        self._se.subscribe_event(
            "dispatch_remove_array_formula",
            self._fn_on_shared_dispatch_dispatch_remove_array_formula,
        )

    def on_shared_dispatch_data_frame_state_before(self, src: Any, event: EventArgs) -> None:
        self._log.debug("on_shared_dispatch_data_frame_state_before() Entering.")

    def on_shared_dispatch_data_frame_state_after(self, src: Any, event: EventArgs) -> None:
        self._log.debug("on_shared_dispatch_data_frame_state_after() Entering.")

    def on_shared_dispatch_added_cell_formula(self, src: Any, event: EventArgs) -> None:
        self._log.debug("on_shared_dispatch_added_cell_formula() Entering.")

    def on_shared_dispatch_removed_cell_formula(self, src: Any, event: EventArgs) -> None:
        self._log.debug("on_shared_dispatch_removed_cell_formula() Entering.")

    def on_shared_dispatch_dispatch_add_array_formula(self, src: Any, event: EventArgs) -> None:
        with self._log.indent(True):
            try:
                self._log.debug("on_shared_dispatch_dispatch_add_array_formula() Entering.")
                sheet = cast(CalcSheet, event.event_data.sheet)
                cr = sheet.get_range(range_obj=event.event_data.range_obj)
                self._style.add_style_range(cr)
            except Exception:
                self._log.error("Error adding array formula style", exc_info=True)

    def on_shared_dispatch_dispatch_remove_array_formula(self, src: Any, event: EventArgs) -> None:
        with self._log.indent(True):
            try:
                self._log.debug("on_shared_dispatch_dispatch_remove_array_formula() Entering.")
                self._log.debug("on_shared_dispatch_dispatch_add_array_formula() Entering.")
                sheet = cast(CalcSheet, event.event_data.sheet)
                cr = sheet.get_range(range_obj=event.event_data.range_obj)
                self._style.remove_style_range(cr)
            except Exception:
                self._log.error("Error removing array formula style", exc_info=True)

    # endregion Shared Events

    def add_cell_control_from_pyc_rule(self, rule: PycRuleT) -> None:
        """
        Add a control to a cell from a PycRule.

        Args:
            rule (PycRuleT): PycRule.
        """
        with self._log.indent(True):
            try:
                self._ctl_mgr.set_ctl_from_pyc_rule(rule)
            except Exception:
                self._log.error("Error setting custom property control", exc_info=True)

    def update_control(self, cell: CalcCell) -> None:
        """
        Updates the control for the cell via the Control Manager.

        Args:
            cell (CalcCell): _description_
        """
        # this method is also called by dispatch.dispatch_toggle_df_state.DispatchToggleDFState
        with self._log.indent(True):
            self._log.debug("update_control() Updating control for cell: %s", cell.cell_obj)
            self._ctl_mgr.update_ctl(cell)
            self._log.debug("update_control() Updated control for cell: %s", cell.cell_obj)

    def _remove_cell(self, calc_cell: CalcCell) -> None:
        """
        Remove a cell.

        Args:
            cell_obj (CellObj): cell object.
        """
        # removing a cell involves:
        # - deleting the cell python code
        # - removing cell from PyInstance
        # - removing cell from CellCache
        # - removing listener from cell
        # - removing custom property from cell
        # - removing cell control.
        # Everything is removed via self.py_inst.remove_source() except removing listener.
        with self._log.indent(True):
            is_deleted = calc_cell.extra_data.get("deleted", False)
            cell_obj = calc_cell.cell_obj
            self._log.debug(f"_remove_cell() Removing cell: {cell_obj}")
            if is_deleted:
                self._log.debug(
                    "Cell is deleted: %s getting code name from deleted cell extra data.",
                    cell_obj,
                )
                code_name = calc_cell.extra_data.code_name
            else:
                if cell_obj.sheet_idx < 0:
                    self._log.error(
                        "Sheet index is less than 0: %i for %s",
                        cell_obj.sheet_idx,
                        cell_obj,
                    )
                    raise ValueError(
                        "Sheet index is less than 0: %i for %s",
                        cell_obj.sheet_idx,
                        cell_obj,
                    )
                if self._cell_cache is None:
                    # this should never happen.
                    self._log.error("Cell cache is None")
                    raise ValueError("Cell cache is None")
                icp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
                code_name = icp.code_name
            try:
                self._log.debug(f"Removing listener from cell: {cell_obj}")
                self._remove_listener_from_cell(calc_cell, code_name)
            except Exception:
                self._log.error("Error removing listener from cell: %s", cell_obj, exc_info=True)

            # don't check using self.is_cell_deleted(calc_cell.component) because it may
            # not be accurate if the cell is deleted.
            # This has to do with how the CodeCellListener() is constructing the CalcCell on Delete.
            # if self.is_cell_deleted(calc_cell.component):
            if is_deleted:
                self._log.debug("Cell is deleted: %s", cell_obj)
                absolute_name = False
            else:
                absolute_name = calc_cell.component.AbsoluteName
                self._log.debug("Cell absolute Name: %s", absolute_name)
            try:
                # remove cell control.
                # CtlMgr can handle cell that are deleted.
                self._ctl_mgr.remove_ctl(calc_cell)
                self._log.debug("Removed cell control for cell: %s", cell_obj)
            except Exception:
                self._log.error(f"Error removing cell control: {cell_obj}", exc_info=True)

            try:
                if absolute_name:
                    py_src_index = self.py_inst.get_index(cell_obj)
                    if py_src_index < 0:
                        self._log.error("Cell does not exist in PyInstance: %s", cell_obj)
                        raise KeyError("Cell does not exist in PyInstance: %s", cell_obj)

                    self.py_inst.remove_source(cell_obj)
                else:
                    self.py_inst.remove_source_by_calc_cell(calc_cell)
            except Exception:
                self._log.error(
                    "Error getting cell index from PyInstance: %s",
                    cell_obj,
                    exc_info=True,
                )

            try:
                if absolute_name:
                    prefix = self._cfg.cell_cp_prefix
                    props = calc_cell.get_custom_properties()
                    for key in props.keys():
                        if key.startswith(prefix):
                            calc_cell.remove_custom_property(key)
                            self._log.debug(
                                "Removed custom property: %s for cell: %s",
                                key,
                                cell_obj,
                            )

            except Exception:
                self._log.error(f"Error removing cell rules: {cell_obj}", exc_info=True)

            self.reset_cell_cache()
            self._log.debug(f"_remove_cell() Removed cell: {cell_obj}")

    def has_cell(self, cell_obj: CellObj) -> bool:
        with self._log.indent(True):
            if cell_obj.sheet_idx < 0:
                self._log.warning(
                    "Sheet index is less than 0: %i for %s",
                    cell_obj.sheet_idx,
                    cell_obj,
                )
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            return self._cell_cache.has_cell(cell_obj, cell_obj.sheet_idx)

    # def trigger_cell_modify_event(self, cell: SheetCell, code_name: str) -> None:
    #     """
    #     Triggers the Modifier event for a cell.

    #     Args:
    #         cell (SheetCell): UNO Cell.
    #         code_name (str): Cell unique id.
    #     """
    #     try:
    #         if not self.has_listener(code_name):
    #             self._log.debug(
    #                 f"Cell '{code_name}' does not have listener. Adding listener to cell: {cell.AbsoluteName}"
    #             )
    #             self._add_listener_to_cell(cell, code_name)
    #         listener = self.get_listener(code_name)
    #         event_obj = EventObject(cell)
    #         listener.modified(event_obj)
    #     except Exception:
    #         self._log.error(f"Error triggering cell modify event for cell: {cell.AbsoluteName}", exc_info=True)

    def add_source_code(self, cell_obj: CellObj, source_code: str) -> None:
        """
        Add source code to a cell.
        """
        with self._log.indent(True):
            if cell_obj.sheet_idx < 0:
                self._log.error(
                    "Sheet index is less than 0: %i for %s",
                    cell_obj.sheet_idx,
                    cell_obj,
                )
                raise ValueError(
                    "Sheet index is less than 0: %i for %s",
                    cell_obj.sheet_idx,
                    cell_obj,
                )
            # adds
            # - source code to cell
            # - custom property to cell
            # - cell to cell cache
            self.py_inst.add_source(code=source_code, cell=cell_obj)
            # at this point the cell custom name can be gotten from CellCache
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            idp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
            self.reset_py_inst()
            sheet = self._doc.sheets[cell_obj.sheet_idx]
            cell = sheet[cell_obj]
            self._add_listener_to_cell(cell, idp.code_name)

    def _add_listener_to_cell(self, cell: CalcCell, name: str) -> None:
        with self._log.indent(True):
            try:
                if name not in self._listeners:
                    # listener = CodeCellListener(cell.AbsoluteName, name)
                    listener = self._listeners.add_listener(cell, name)
                    if listener is None:
                        if self._is_db:
                            self._log.error(
                                "Error creating listener for cell: %s with codename %s.",
                                cell.cell_obj,
                                name,
                            )
                        return
                    self._listener_subscribe(listener)
                    if self._is_db:
                        self._log.debug(
                            "Added listener to cell: %s with codename %s.",
                            cell.cell_obj,
                            name,
                        )
                else:
                    self._log.error(f"Listener already exists for cell: {cell.cell_obj} with codename {name}.")
            except Exception:
                self._log.error(
                    "Error adding listener to cell:%s} with codename %s.",
                    cell.cell_obj,
                    name,
                    exc_info=True,
                )

    def _remove_listener_from_cell(self, cell: CalcCell, name: str) -> None:
        with self._log.indent(True):
            try:
                if name in self._listeners:
                    listener = self._listeners[name]
                    self._listener_unsubscribe(listener)
                    self._listeners.remove_listener(cell, name)
                else:
                    self._log.error("Listener does not exists for cell with codename %s", name)
            except Exception:
                self._log.error(
                    "Error removing listener from cell with codename %s.",
                    name,
                    exc_info=True,
                )

    def _listener_subscribe(self, listener: CodeCellListener) -> None:
        listener.subscribe_cell_deleted(self._fn_on_cell_deleted)
        listener.subscribe_cell_modified(self._fn_on_cell_modified)
        listener.subscribe_cell_moved(self._fn_on_cell_moved)
        listener.subscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
        listener.subscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)

    def _listener_unsubscribe(self, listener: CodeCellListener) -> None:
        listener.unsubscribe_cell_deleted(self._fn_on_cell_deleted)
        listener.unsubscribe_cell_modified(self._fn_on_cell_modified)
        listener.unsubscribe_cell_moved(self._fn_on_cell_moved)
        listener.unsubscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
        listener.unsubscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)

    def is_cell_deleted(self, cell: SheetCell) -> bool:
        """Gets if a sheet cell has been deleted."""
        ci = CellInfo(cell)
        return ci.is_cell_deleted()

    def add_all_listeners(self) -> None:
        """
        Add all listeners for the current cells.

        Note:
            This method only add listeners managed by the ``CellMgr`` Class.
            This method will not add or remove actual Listeners from the cells, use ``CodeCellListeners`` for that.
        """
        with self._log.indent(True):
            for listener in self._listeners.values():
                self._listener_unsubscribe(listener)
                self._listener_subscribe(listener)
            self._log.debug(f"Added {len(self._listeners)} listeners")

    def remove_all_listeners(self) -> None:
        """
        Remove all listeners.

        For all current listeners they are removed from the cells.

        Note:
            This method only removes listeners managed by the ``CellMgr`` Class.
            This method will not add or remove actual Listeners from the cells, use ``CodeCellListeners`` for that.
        """
        with self._log.indent(True):
            self._log.debug("Removing all listeners")
            for listener in self._listeners.values():
                self._listener_unsubscribe(listener)
            self._log.debug("Removed all listeners")

    def get_listener(self, code_name: str) -> CodeCellListener:
        """
        Get a listener for a cell.

        Args:
            code_name (str): code name of cell.
        """
        with self._log.indent(True):
            listener = self._listeners.get(code_name)
            if listener is None:
                self._log.error("Listener does not exist for code name: %s", code_name)
                raise KeyError(f"Listener does not exist for code name: {code_name}")
            return listener

    def has_listener(self, code_name: str) -> bool:
        """
        Check if a listener exists for a cell.

        Args:
            code_name (str): code name of cell.
        """
        return code_name in self._listeners

    # def get_all_listeners(self) -> dict[str, CodeCellListener]:
    #     """
    #     Get all listeners.
    #     """
    #     return self._listeners

    def is_first_cell(self, cell_obj: CellObj) -> bool:
        """
        Check if the current cell is the first cell in the sheet.
        """
        with self._log.indent(True):
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            return self._cell_cache.is_first_cell(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)

    def is_last_cell(self, cell_obj: CellObj) -> bool:
        """
        Check if the current cell is the last cell in the sheet.
        """
        with self._log.indent(True):
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            return self._cell_cache.is_last_cell(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)

    def reset_py_inst(self, update_display: bool = False) -> None:
        """
        Reset the PyInstance.

        Args:
            update_display (bool, optional): Update the display after reset. Defaults to False.

        Note:
            Updating display will toggle the sheet python arrays on and off.
        """
        update_display = False
        with self._log.indent(True):
            self._log.debug("reset_py_inst() Resetting PyInstance")
            self._py_inst = None
            PyInstance.reset_instance(self._doc)
            if update_display:
                self.py_inst.unsubscribe_after_update_source(self._fn_py_inst_after_source_update)
                self.py_inst.subscribe_after_source_update(self._fn_py_inst_after_source_update)
            self.py_inst.update_all()
            if update_display:
                self.py_inst.unsubscribe_after_update_source(self._fn_py_inst_after_source_update)
            self._log.debug("reset_py_inst() Done")

    def _py_inst_after_source_update(self, src: Any, event: EventArgs) -> None:
        # event data is DotDict(
        # source=self,
        # sheet_idx=sheet_idx,
        # row=row,
        # col=col,
        # code=code,
        # doc=self._doc,
        # py_src=py_src,
        # )
        self._log.debug("PyInstance after source update")
        doc = cast(CalcDoc, event.event_data.doc)
        sheet_idx = cast(int, event.event_data.sheet_idx)
        row = cast(int, event.event_data.row)
        col = cast(int, event.event_data.col)
        co = CellObj.from_idx(col_idx=col, row_idx=row, sheet_idx=sheet_idx)
        cc = doc.sheets[sheet_idx][co]

        cds = CellDispatchState(cell=cc)
        # if not cds.is_dispatch_enabled():
        #     return
        state = cds.get_state()

        # lp = LplCell(cc)
        # state = lp.ctl_state
        if state == StateKind.ARRAY:
            # lp.ctl_state = StateKind.PY_OBJ
            # lp.ctl_state = StateKind.ARRAY
            # dpc = f".uno:libre_pythonista.calc.py_obj.state?sheet={cc.calc_sheet.name}&cell={co}"
            dpc = f"{UNO_DISPATCH_PY_OBJ_STATE}?sheet={cc.calc_sheet.name}&cell={co}"
            doc.dispatch_cmd(dpc)
            rule_dpc = cds.get_rule_dispatch_cmd()
            if rule_dpc:
                doc.dispatch_cmd(rule_dpc)

        self._log.debug("PyInstance after source update Done")

    def reset_cell_cache(self) -> None:
        """
        Reset the cell cache.
        """
        with self._log.indent(True):
            self._log.debug("Resetting cell cache")
            self._cell_cache = None
            CellCache.reset_instance(self._doc)
            self._cell_cache = CellCache(self._doc)  # singleton
            self._log.debug("Reset cell cache")

    def get_py_src(self, cell_obj: CellObj) -> PySource:
        """
        Get the PySource for a cell.
        """
        is_db = self._log.is_debug
        with self._log.indent(True):
            if is_db:
                self._log.debug("get_py_src() Getting PySource for cell: %s", cell_obj)
            result = self.py_inst[cell_obj]
            if is_db:
                self._log.debug("get_py_src() Got PySource for cell: %s", cell_obj)
            return result

    def update_from_cell_obj(self, cell_obj: CellObj) -> None:
        """
        Update the PyInstance from a cell object. This will update the PyInstance with the latest code for the cell and all cells that come after.

        Args:
            cell_obj (CellObj): cell object.
        """
        with self._log.indent(True):
            self._log.debug(f"update_from_cell_obj() - Updating PyInstance from cell object: {cell_obj}")
            index = self.py_inst.get_index(cell_obj)
            if index < 0:
                self._log.error("Cell does not exist in PyInstance: %s", cell_obj)
                raise KeyError(f"Cell does not exist in PyInstance: {cell_obj}")
            self._log.debug(f"update_from_cell_obj() - Index: {index}")
            self.py_inst.update_from_index(index)
            self._log.debug(f"update_from_cell_obj() - Updated PyInstance from cell object: {cell_obj}")

    def set_global_var(self, name: str, value: Any) -> None:
        """
        Set a global variable in the module.

        Args:
            name (str): Variable name.
            value (Any): Variable value.
        """
        with self._log.indent(True):
            self._log.debug(f"set_global_var() - Setting Global Variable: {name}")
            self.py_inst.set_global_var(name, value)

    def update_sheet_cell_addr_prop(self, sheet_idx: int) -> None:
        """
        Updates the cell address custom property for the cells in the sheet.

        Args:
            sheet_idx (int, optional): Sheet Index. Defaults to ``current_sheet_index``.

        Warning:
            This method need to be run on a up to date cell cache.
            Usually ``reset_instance`` is call before running this method.

            See ``CellCache.update_sheet_cell_addr_prop()`` for more.
        """
        with self._log.indent(True):
            if not self._cell_cache:
                self._log.error("Cell cache is None")
                return None

            self._cell_cache.update_sheet_cell_addr_prop(sheet_idx)

    @contextmanager
    def listener_context(self, cell: SheetCell):
        """
        Context manager that on entry removes the listener for a cell if the listener exists.
        On exit the listener is added back to the cell if it existed.
        """

        self._log.debug(f"Listener context for cell: {cell.AbsoluteName}")
        listener = None
        code_name = ""
        try:
            self._log.indent(False)
            # get the code name
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            address = cell.getCellAddress()
            cell_obj = CellObj.from_idx(col_idx=address.Column, row_idx=address.Row, sheet_idx=address.Sheet)

            icp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
            code_name = icp.code_name
            if code_name in self._listeners:
                self._log.debug("Un-subscribing listeners for cell: %s", cell.AbsoluteName)
                listener = self._listeners[code_name]
                listener.unsubscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.unsubscribe_cell_modified(self._fn_on_cell_modified)
                listener.unsubscribe_cell_moved(self._fn_on_cell_moved)
                listener.unsubscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.unsubscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                # cell.removeModifyListener(listener)
            else:
                self._log.debug("Listener does not exist for cell: %s", cell.AbsoluteName)
            yield
        finally:
            if listener is not None:
                self._log.debug("Subscribing to listeners for cell: %s", cell.AbsoluteName)
                listener.subscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.subscribe_cell_modified(self._fn_on_cell_modified)
                listener.subscribe_cell_moved(self._fn_on_cell_moved)
                listener.subscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.subscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                self._listeners[code_name] = listener
                # cell.addModifyListener(listener)
            self._log.outdent()

    @property
    def py_inst(self) -> PySourceManager:
        if self._py_inst is None:
            self._py_inst = PyInstance(self._doc)
            self._py_inst.subscribe_after_update_source(self._fn_on_py_code_updated)
        return self._py_inst

    @property
    def log(self) -> OxtLogger:
        return self._log

    @classmethod
    def reset_instance(cls, doc: CalcDoc) -> None:
        """
        Reset the Singleton instance(s).

        Args:
            doc (CalcDoc): Calc Doc or None. If None all cached instances are cleared. Defaults to None.
        """
        log = LogInst()
        if cls.has_singleton_instance:
            log.debug(
                "CellMgr.reset_instance() - Resetting instance for doc: %s",
                doc.runtime_uid,
            )
            inst = cls(doc)
            cls.remove_this_instance(inst)
        else:
            log.debug(
                "CellMgr.reset_instance() - No instance to reset for doc: %s",
                doc.runtime_uid,
            )

        PyInstance.reset_instance(doc)
        CellCache.reset_instance(doc)


@check_breakpoint("update_array_cells")
def update_array_cells(doc: Any):
    # this method is called by CellMgr._on_pyc_rule_matched() in a separate thread.
    # this method calls ArrayMgr.update_array_cells(),
    # which is responsible for updating the array formula for the cells if the array size has changed.
    am = ArrayMgr(doc)
    am.update_array_cells()
