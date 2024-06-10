"""
Manages the code cells.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
from contextlib import contextmanager
import uno
from ooodev.calc import CalcDoc, CalcCell, CalcSheet
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from .listen.code_cell_listener import CodeCellListener
from ..code.cell_cache import CellCache
from ..code.py_source_mgr import PyInstance
from ..code.py_source_mgr import PySource


if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
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
        self._fn_on_cell_modified = self.on_cell_modified

    def on_cell_deleted(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is deleted.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str

        """
        dd = cast(DotDict, event.event_data)
        self._remove_listener_from_cell(dd.event_obj.Source, dd.code_name)
        self._log.debug(f"Cell deleted: {dd.absolute_name}")

    def on_cell_moved(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is deleted.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: current cell absolute name.
        - old_name: old cell absolute name.
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str

        """
        dd = cast(DotDict, event.event_data)
        self.reset_cell_cache()
        self._log.debug(f"Cell moved: {dd.absolute_name}")

    def on_cell_modified(self, src: Any, event: EventArgs) -> None:
        """
        Event handler for when a cell is modified.

        ``EventArgs.event_data`` is a DotDict with the following keys:
        - absolute_name: str
        - event_obj: ``com.sun.star.lang.EventObject``
        - code_name: str

        """
        dd = cast(DotDict, event.event_data)
        try:
            cell = cast("SheetCell", dd.event_obj.Source)
            formula = cell.getFormula()
            if formula:
                s = formula.lstrip("=")  # formula may start with one or two equal signs
            else:
                s = ""
            if not s.startswith("COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.PYIMPL.PYC"):
                self._log.debug(
                    f"Formula has been modified or removed. Not a LibrePythonista cell: {dd.absolute_name}"
                )
                address = cell.getCellAddress()
                cell_obj = CellObj.from_idx(col_idx=address.Column, row_idx=address.Row, sheet_idx=address.Sheet)
                self._remove_cell(cell_obj=cell_obj, cell=cell)

        except Exception:
            self._log.error(f"Error modifying cell: {dd.absolute_name}", exc_info=True)

        self._log.debug(f"Cell modified: {dd.absolute_name}")

    # endregion Cell Events

    def _remove_cell(self, cell_obj: CellObj, cell: SheetCell) -> None:
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
        # Everythhing is removed via self._py_inst.remove_source() except removing listener.
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
            py_src_index = self._py_inst.get_index(cell_obj)
            if py_src_index < 0:
                self._log.error(f"Cell does not exist in PyInstance: {cell_obj}")
                raise KeyError(f"Cell does not exist in PyInstance: {cell_obj}")

            self._py_inst.remove_source(cell_obj)
        except Exception:
            self._log.error(f"Error getting cell index from PyInstance: {cell_obj}", exc_info=True)

        self._remove_listener_from_cell(cell, code_name)

    def has_cell(self, cell_obj: CellObj) -> bool:
        if cell_obj.sheet_idx < 0:
            self._log.warning(f"Sheet index is less than 0: {cell_obj.sheet_idx} for {cell_obj}")
        if self._cell_cache is None:
            # this should never happen.
            self._log.error("Cell cache is None")
            raise ValueError("Cell cache is None")
        return self._cell_cache.has_cell(cell_obj, cell_obj.sheet_idx)

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
                cell.removeModifyListener(listener)
                self._log.debug(f"Removed listener from cell with codename {name}.")
            else:
                self._log.error(f"Listener does not exists for cell with codename {name}.")
        except Exception:
            self._log.error(f"Error removing listener from cell with codename {name}.", exc_info=True)

    def add_all_listeners(self) -> None:
        """
        Add all listeners for the current cells.
        """
        self._log.debug("Adding all listeners")
        if self._listeners:
            self._log.warning("Listeners already exist. Not adding listeners.")
            return
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
