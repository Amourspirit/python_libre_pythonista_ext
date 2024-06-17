"""
Manages the code cells.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import contextlib
from contextlib import contextmanager
import uno
from com.sun.star.uno import RuntimeException
from ooo.dyn.lang.event_object import EventObject
from ooodev.calc import CalcDoc, CalcCell, CalcSheet
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from .listen.code_cell_listener import CodeCellListener
from ..code.cell_cache import CellCache
from ..code.py_source_mgr import PyInstance
from ..code.py_source_mgr import PySource
from ..cell.ctl.ctl_mgr import CtlMgr
from ..cell.result_action.pyc.rules.pyc_rules import PycRules
from ..cell.cell_info import CellInfo

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
    from .result_action.pyc.rules.pyc_rule_t import PycRuleT
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


class CellMgr:
    _instances: Dict[str, CellMgr] = {}

    def __new__(cls, doc: CalcDoc):
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            cls._instances[key] = super(CellMgr, cls).__new__(cls)
            cls._instances[key]._is_init = False
        return cls._instances[key]

    def __init__(self, doc: CalcDoc):
        is_init = getattr(self, "_is_init", False)
        if is_init:
            return
        self._cfg = Config()
        self._doc = doc
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug(f"init for doc: {doc.runtime_uid}")
        self._listeners = {}  # type: dict[str, CodeCellListener]
        self._cell_cache = CellCache(doc)  # singleton
        self._py_inst = PyInstance(doc)  # singleton
        self._init_events()
        self._is_init = True

    # region Cell Events
    def _init_events(self) -> None:
        self._fn_on_cell_deleted = self.on_cell_deleted
        self._fn_on_cell_moved = self.on_cell_moved
        self._fn_on_cell_pyc_formula_removed = self.on_cell_pyc_formula_removed
        self._fn_on_cell_modified = self.on_cell_modified
        self._fn_on_cell_custom_prop_modify = self.on_cell_custom_prop_modify

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


        """
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
        - deleted: False

        """
        dd = cast(DotDict, event.event_data)
        self.reset_cell_cache()
        self._log.debug(f"Cell moved: {dd.absolute_name}")

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
        try:
            self._log.debug("on_cell_pyc_formula_removed() Entering.")
            dd = cast(DotDict, event.event_data)
            self._remove_cell(calc_cell=dd.calc_cell)
            self._log.debug(f"on_cell_pyc_formula_removed() Leaving: {dd.absolute_name}")
        except Exception:
            self._log.error(f"Error removing pyc formula from cell: {dd.absolute_name}", exc_info=True)

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

        """
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

    def add_cell_control_from_pyc_rule(self, rule: PycRuleT) -> None:
        """
        Add a control to a cell from a PycRule.

        Args:
            rule (PycRuleT): PycRule.
        """
        try:
            ct_mgr = CtlMgr()
            ct_mgr.set_ctl_from_pyc_rule(rule)
        except Exception:
            self._log.error("Error setting custom property control", exc_info=True)

    def update_control(self, cell: CalcCell) -> None:
        """
        Updates the control for the cell via the Control Manager.

        Args:
            cell (CalcCell): _description_
        """
        # this method is also called by dispatch.dispatch_toggle_df_state.DispatchToggleDFState
        self._log.debug(f"update_control() Updating control for cell: {cell.cell_obj}")
        ct_mgr = CtlMgr()
        ct_mgr.update_ctl(cell)
        self._log.debug(f"update_control() Updated control for cell: {cell.cell_obj}")

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
        # Everything is removed via self._py_inst.remove_source() except removing listener.
        is_deleted = calc_cell.extra_data.get("deleted", False)
        cell_obj = calc_cell.cell_obj
        self._log.debug(f"_remove_cell() Removing cell: {cell_obj}")
        if is_deleted:
            self._log.debug(f"Cell is deleted: {cell_obj} getting code name from deleted cell extra data.")
            code_name = calc_cell.extra_data.code_name
        else:
            if cell_obj.sheet_idx < 0:
                self._log.error(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
                raise ValueError(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            icp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
            code_name = icp.code_name
        try:
            self._log.debug(f"Removing listener from cell: {cell_obj}")
            self._remove_listener_from_cell(calc_cell.component, code_name)
        except:
            self._log.error(f"Error removing listener from cell: {cell_obj}", exc_info=True)

        # don't check using self.is_cell_deleted(calc_cell.component) because it may
        # not be accurate if the cell is deleted.
        # This has to do with how the CodeCellListener() is constructing the CalcCell on Delete.
        # if self.is_cell_deleted(calc_cell.component):
        if is_deleted:
            self._log.debug(f"Cell is deleted: {cell_obj}")
            absolute_name = False
        else:
            absolute_name = calc_cell.component.AbsoluteName
            self._log.debug(f"Cell absolute Name: {absolute_name}")
        try:
            # remove cell control.
            # CtlMgr can handle cell that are deleted.
            ctl_mgr = CtlMgr()
            ctl_mgr.remove_ctl(calc_cell)
            self._log.debug(f"Removed cell control for cell: {cell_obj}")
        except Exception:
            self._log.error(f"Error removing cell control: {cell_obj}", exc_info=True)

        try:
            if absolute_name:
                py_src_index = self._py_inst.get_index(cell_obj)
                if py_src_index < 0:
                    self._log.error(f"Cell does not exist in PyInstance: {cell_obj}")
                    raise KeyError(f"Cell does not exist in PyInstance: {cell_obj}")

                self._py_inst.remove_source(cell_obj)
            else:
                self._py_inst.remove_source_by_calc_cell(calc_cell)
        except Exception:
            self._log.error(f"Error getting cell index from PyInstance: {cell_obj}", exc_info=True)

        try:
            if absolute_name:
                prefix = self._cfg.cell_cp_prefix
                props = calc_cell.get_custom_properties()
                for key in props.keys():
                    if key.startswith(prefix):
                        calc_cell.remove_custom_property(key)
                        self._log.debug(f"Removed custom property: {key} for cell: {cell_obj}")

        except Exception:
            self._log.error(f"Error removing cell rules: {cell_obj}", exc_info=True)

        self.reset_cell_cache()
        self._log.debug(f"_remove_cell() Removed cell: {cell_obj}")

    def has_cell(self, cell_obj: CellObj) -> bool:
        if cell_obj.sheet_idx < 0:
            self._log.warning(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
        if self._cell_cache is None:
            # this should never happen.
            self._log.error("Cell cache is None")
            raise ValueError("Cell cache is None")
        return self._cell_cache.has_cell(cell_obj, cell_obj.sheet_idx)

    def trigger_cell_modify_event(self, cell: SheetCell, code_name: str) -> None:
        """
        Triggers the Modifier event for a cell.

        Args:
            cell (SheetCell): UNO Cell.
            code_name (str): Cell unique id.
        """
        try:
            # cell_addr = cell.getCellAddress()
            # cell_obj = CellObj.from_idx(col_idx=cell_addr.Column, row_idx=cell_addr.Row, sheet_idx=cell_addr.Sheet)
            if not self.has_listener(code_name):
                self._log.debug(
                    f"Cell '{code_name}' does not have listener. Adding listener to cell: {cell.AbsoluteName}"
                )
                self._add_listener_to_cell(cell, code_name)
            listener = self.get_listener(code_name)
            event_obj = EventObject(cell)
            listener.modified(event_obj)
        except Exception:
            self._log.error(f"Error triggering cell modify event for cell: {cell.AbsoluteName}", exc_info=True)

    def add_source_code(self, cell_obj: CellObj, source_code: str) -> None:
        """
        Add source code to a cell.
        """
        if cell_obj.sheet_idx < 0:
            self._log.error(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
            raise ValueError(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
        # adds
        # - source code to cell
        # - custom property to cell
        # - cell to cell cache
        self._py_inst.add_source(code=source_code, cell=cell_obj)
        # at this point the cell custom name can be gotten from CellCache
        if self._cell_cache is None:
            # this should never happen.
            self._log.error("Cell cache is None")
            raise ValueError("Cell cache is None")
        idp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
        self.reset_py_inst()
        sheet = self._doc.sheets[cell_obj.sheet_idx]
        cell = sheet[cell_obj]
        self._add_listener_to_cell(cell.component, idp.code_name)

    def _add_listener_to_cell(self, cell: SheetCell, name: str) -> None:
        try:
            if name not in self._listeners:
                listener = CodeCellListener(cell.AbsoluteName, name)
                self._listeners[name] = listener
                listener.subscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.subscribe_cell_modified(self._fn_on_cell_modified)
                listener.subscribe_cell_moved(self._fn_on_cell_moved)
                listener.subscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.subscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                cell.addModifyListener(listener)
                self._log.debug(f"Added listener to cell: {cell.AbsoluteName} with codename {name}.")
            else:
                self._log.error(f"Listener already exists for cell: {cell.AbsoluteName} with codename {name}.")
        except Exception:
            self._log.error(f"Error adding listener to cell: {cell.AbsoluteName} with codename {name}.", exc_info=True)

    def _remove_listener_from_cell(self, cell: SheetCell, name: str) -> None:
        try:
            if name in self._listeners:
                listener = self._listeners[name]
                listener.unsubscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.unsubscribe_cell_modified(self._fn_on_cell_modified)
                listener.unsubscribe_cell_moved(self._fn_on_cell_moved)
                listener.unsubscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.unsubscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                if not self.is_cell_deleted(cell):
                    cell.removeModifyListener(listener)
                    self._log.debug(f"Removed listener from cell with codename {name}.")
                else:
                    self._log.debug(f"Cell with codename {name} has been deleted. Not removing listener.")
            else:
                self._log.error(f"Listener does not exists for cell with codename {name}.")
        except Exception:
            self._log.error(f"Error removing listener from cell with codename {name}.", exc_info=True)

    def is_cell_deleted(self, cell: SheetCell) -> bool:
        """Gets if a sheet cell has been deleted."""
        ci = CellInfo(cell)
        return ci.is_cell_deleted()

    def add_all_listeners(self) -> None:
        """
        Add all listeners for the current cells.
        """
        self._log.debug("Adding all listeners")
        if self._listeners:
            self._log.warning("Listeners already exist. Not adding listeners.")
            return
        assert self._cell_cache is not None, "Cell cache is None"
        cc = self._cell_cache.code_cells
        i = 0
        for sheet_idx, obj in cc.items():
            sheet = self._doc.sheets[sheet_idx]
            for cell_obj, cell_prop_idx in obj.items():
                cell = sheet[cell_obj]
                self._add_listener_to_cell(cell.component, cell_prop_idx.code_name)
                i += 1
        self._log.debug(f"Added {i} listeners")

    def remove_all_listeners(self) -> None:
        """
        Remove all listeners.

        For all current listeners they are removed from the cells.
        """
        self._log.debug("Removing all listeners")
        sheet_cells = {}
        # gather cells by sheet
        for name in self._listeners.keys():
            assert self._cell_cache is not None, "Cell cache is None"
            cell_obj = self._cell_cache.code_name_cell_map.get(name, None)
            if cell_obj is None:
                self._log.error(f"Cell object does not exist for code name: {name}")
                continue
            if cell_obj.sheet_idx not in sheet_cells:
                sheet_cells[cell_obj.sheet_idx] = []

            sheet_cells[cell_obj.sheet_idx].append((name, cell_obj))

        for sheet_idx, obj in sheet_cells.items():
            sheet = self._doc.sheets[sheet_idx]
            for name, cell_obj in obj:
                cell = sheet[cell_obj]
                self._remove_listener_from_cell(cell.component, name)

        self._listeners.clear()
        self._log.debug("Removed all listeners")

    def get_listener(self, code_name: str) -> CodeCellListener:
        """
        Get a listener for a cell.

        Args:
            code_name (str): code name of cell.
        """
        listener = self._listeners.get(code_name, None)
        if listener is None:
            self._log.error(f"Listener does not exist for code name: {code_name}")
            raise KeyError(f"Listener does not exist for code name: {code_name}")
        return listener

    def has_listener(self, code_name: str) -> bool:
        """
        Check if a listener exists for a cell.

        Args:
            code_name (str): code name of cell.
        """
        return code_name in self._listeners

    def get_all_listeners(self) -> dict[str, CodeCellListener]:
        """
        Get all listeners.
        """
        return self._listeners

    def is_first_cell(self, cell_obj: CellObj) -> bool:
        """
        Check if the current cell is the first cell in the sheet.
        """
        if self._cell_cache is None:
            # this should never happen.
            self._log.error("Cell cache is None")
            raise ValueError("Cell cache is None")
        return self._cell_cache.is_first_cell(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)

    def reset_py_inst(self) -> None:
        """
        Reset the PyInstance.
        """
        self._log.debug("Resetting PyInstance")
        PyInstance.reset_instance(self._doc)
        self._py_inst = PyInstance(self._doc)  # singleton
        self._py_inst.update_all()
        self._log.debug("Reset PyInstance")

    def reset_cell_cache(self) -> None:
        """
        Reset the cell cache.
        """
        self._log.debug("Resetting cell cache")
        self._cell_cache = None
        CellCache.reset_instance(self._doc)
        self._cell_cache = CellCache(self._doc)  # singleton
        self._log.debug("Reset cell cache")

    def get_py_src(self, cell_obj: CellObj) -> PySource:
        """
        Get the PySource for a cell.
        """
        return self._py_inst[cell_obj]

    def update_from_cell_obj(self, cell_obj: CellObj) -> None:
        """
        Update the PyInstance from a cell object. This will update the PyInstance with the latest code for the cell and all cells that come after.

        Args:
            cell_obj (CellObj): cell object.
        """
        self._log.debug(f"update_from_cell_obj() - Updating PyInstance from cell object: {cell_obj}")
        index = self._py_inst.get_index(cell_obj)
        if index < 0:
            self._log.error(f"Cell does not exist in PyInstance: {cell_obj}")
            raise KeyError(f"Cell does not exist in PyInstance: {cell_obj}")
        self._log.debug(f"update_from_cell_obj() - Index: {index}")
        self._py_inst.update_from_index(index)
        self._log.debug(f"update_from_cell_obj() - Updated PyInstance from cell object: {cell_obj}")

    def set_global_var(self, name: str, value: Any) -> None:
        """
        Set a global variable in the module.

        Args:
            name (str): Variable name.
            value (Any): Variable value.
        """
        self._log.debug(f"set_global_var() - Setting Global Variable: {name}")
        self._py_inst.set_global_var(name, value)

    @contextmanager
    def listener_context(self, cell: SheetCell):
        """
        Context manager that on entry removes the listener for a cell if the listener exists.
        On exit the listener is added back to the cell if it existed.
        """
        self._log.debug(f"Listener context for cell: {cell.AbsoluteName}")
        try:
            # get the code name
            if self._cell_cache is None:
                # this should never happen.
                self._log.error("Cell cache is None")
                raise ValueError("Cell cache is None")
            address = cell.getCellAddress()
            cell_obj = CellObj.from_idx(col_idx=address.Column, row_idx=address.Row, sheet_idx=address.Sheet)

            icp = self._cell_cache.get_index_cell_props(cell=cell_obj, sheet_idx=cell_obj.sheet_idx)
            code_name = icp.code_name
            listener = None
            if code_name in self._listeners:
                self._log.debug(f"Un-subscribing listeners for cell: {cell.AbsoluteName}")
                listener = self._listeners.pop(code_name)
                listener.unsubscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.unsubscribe_cell_modified(self._fn_on_cell_modified)
                listener.unsubscribe_cell_moved(self._fn_on_cell_moved)
                listener.unsubscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.unsubscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                # cell.removeModifyListener(listener)
            else:
                self._log.debug(f"Listener does not exist for cell: {cell.AbsoluteName}")
            yield
        finally:
            if listener is not None:
                self._log.debug(f"Subscribing to listeners for cell: {cell.AbsoluteName}")
                listener.subscribe_cell_deleted(self._fn_on_cell_deleted)
                listener.subscribe_cell_modified(self._fn_on_cell_modified)
                listener.subscribe_cell_moved(self._fn_on_cell_moved)
                listener.subscribe_cell_custom_prop_modify(self._fn_on_cell_custom_prop_modify)
                listener.subscribe_cell_pyc_formula_removed(self._fn_on_cell_pyc_formula_removed)
                self._listeners[code_name] = listener
                # cell.addModifyListener(listener)

    @classmethod
    def reset_instance(cls, doc: CalcDoc | None = None) -> None:
        """
        Reset the cached instance(s).

        Args:
            doc (CalcDoc | None, optional): Calc Doc or None. If None all cached instances are cleared. Defaults to None.
        """
        if doc is None:
            cls._instances = {}
            return
        key = f"doc_{doc.runtime_uid}"
        if key in cls._instances:
            inst = cls._instances[key]
            try:
                inst.remove_all_listeners()
            except Exception:
                inst._log.error(f"Error removing listeners for doc: {doc.runtime_uid}", exc_info=True)
            inst._log.debug(f"Resetting instance for doc: {doc.runtime_uid}")
            inst._log.debug(f"Resetting cell cache for doc: {doc.runtime_uid}")
            if inst._cell_cache:
                inst._cell_cache.reset_instance(doc)
            inst._log.debug(f"Resetting PyInstance for doc: {doc.runtime_uid}")
            del cls._instances[key]
        PyInstance.reset_instance(doc)
        CellCache.reset_instance(doc)
