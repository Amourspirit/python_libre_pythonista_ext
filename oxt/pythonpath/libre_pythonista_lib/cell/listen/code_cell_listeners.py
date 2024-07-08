from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
import uno
from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcCell, CellObj
from ...code.cell_cache import CellCache
from ...utils.singleton_base import SingletonBase
from ..cell_info import CellInfo
from ..props.key_maker import KeyMaker
from .code_cell_listener import CodeCellListener

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CodeCellListeners(SingletonBase):
    """Singleton Class that tracks all CodeCellListeners for the current document."""

    # singleton ensure separate instances for each document.
    def __init__(self):
        """
        Constructor

        All Cells in the current Cell cache will get listeners attache when this class is instantiated.
        """
        if getattr(self, "_is_init", False):
            return
        # self.singleton_doc = Lo.current_doc
        self._listeners: Dict[str, CodeCellListener] = {}
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Init")
        self._add_all_listeners()
        self._is_init = True

    def __contains__(self, key: str) -> bool:
        return key in self._listeners

    def __getitem__(self, key: str) -> CodeCellListener:
        return self._listeners[key]

    def __setitem__(self, key: str, value: CodeCellListener) -> None:
        try:
            cell = self._get_calc_cell(value.cell_obj)
            if cell is not None:
                # attempt to remove the listener just in case it has been added.
                cell.component.removeModifyListener(value)
                cell.component.addModifyListener(value)
                self._listeners[key] = value
            else:
                self._log.error(f"Cell not found: {value.cell_obj}")

        except Exception:
            self._log.exception(f"Error setting listener: {key}")

    def __delitem__(self, key: str) -> None:
        # a check should be done to ensure the cell has not been deleted before calling this method.
        try:
            if not key in self:
                self._log.error(f"Key not found: {key}")
                return
            listener = self._listeners[key]
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                cell.component.removeModifyListener(listener)
            else:
                self._log.error(f"Cell not found: {listener.cell_obj}")

            del self._listeners[key]
        except Exception:
            self._log.exception(f"Error deleting listener: {key}")

    def __iter__(self):
        return iter(self._listeners)

    def __len__(self) -> int:
        return len(self._listeners)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"

    def items(self):
        """Returns all items in the dictionary in a set like object."""
        return self._listeners.items()

    def keys(self):
        """Returns all keys in the dictionary in a set like object."""
        return self._listeners.keys()

    def values(self):
        """Returns an object providing a view on the dictionary's values."""
        return self._listeners.values()

    def clear(self):
        """Clears the dictionary"""
        self._log.debug("Clearing all listeners")
        self._listeners.clear()

    def _add_all_listeners(self) -> None:
        """
        Add all listeners for the current cells.
        """
        self._log.debug("Adding all listeners")
        doc = cast(CalcDoc, self.singleton_doc)
        cell_cache = CellCache(doc)
        cc = cell_cache.code_cells
        for sheet_idx, cell_idx_props in cc.items():
            sheet = doc.sheets[sheet_idx]
            for cell_obj, cell_prop_idx in cell_idx_props.items():
                cell = sheet[cell_obj]
                listener = CodeCellListener(
                    absolute_name=cell.component.AbsoluteName,
                    code_name=cell_prop_idx.code_name,
                    cell_obj=cell_obj.copy(),
                    listeners=self,
                )
                self[cell_prop_idx.code_name] = listener
                cell.component.addModifyListener(listener)

        self._log.debug(f"Added {len(self)} listeners")

    def _get_calc_cell(self, cell_obj: CellObj) -> CalcCell | None:
        """
        Get the cell object from the cell component.
        """
        if cell_obj.sheet_idx < 0:
            self._log.error(f"Invalid sheet index: {cell_obj.sheet_idx}")
            return None
        doc = cast(CalcDoc, self.singleton_doc)
        sheet = doc.sheets[cell_obj.sheet_idx]
        return sheet[cell_obj]

    def get_cell_listener(self, cell_obj: CellObj) -> CodeCellListener | None:
        """
        Get the listener for a given cell.

        Args:
            cell_obj: The cell object to get the listener for.

        If the code name is known then use ``inst[code_name]`` instead.
        """
        cell = self._get_calc_cell(cell_obj)
        if cell is None:
            self._log.warning(f"Cell not found: {cell_obj}. Returning None")
            return None
        km = KeyMaker()
        code_name = cell.get_custom_property(km.cell_code_name, "")
        if not code_name:
            self._log.warning(f"Cell has no code name: {cell_obj}. Returning None")
            return None
        if code_name not in self:
            self._log.warning(f"Cell listener not found: {code_name}. Returning None")
            return None
        return self[code_name]

    def get(self, code_name: str) -> CodeCellListener | None:
        """
        Get a listener by the code name.

        Args:
            code_name (str): The code name of the listener to get.

        Returns:
            CodeCellListener | None: The listener object or None if not found.
        """
        if code_name in self:
            return self[code_name]
        self._log.warning(f"Listener not found: {code_name}")
        return None

    def pop(self, code_name: str) -> CodeCellListener | None:
        """
        Remove a listener by the code name.

        Args:
            code_name (str): The code name of the listener to remove.

        Returns:
            CodeCellListener | None: The listener object or None if not found.
        """
        if code_name in self:
            listener = self[code_name]
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                cell.component.removeModifyListener(listener)
            else:
                self._log.error(f"Cell not found: {listener.cell_obj}")
            del self._listeners[code_name]
            return listener
        self._log.warning(f"Listener not found: {code_name}")
        return None

    def add_listener(self, cell: CalcCell, code_name: str) -> CodeCellListener | None:
        """
        Adds a Listener to a cell.

        Args:
            cell (CalcCell): The cell to add the listener to.
            code_name (str): The code name for the listener.

        Returns:
            CodeCellListener | None: The listener object or None if failed.
        """
        try:
            if code_name in self:
                self._log.error(f"Listener already exists: {code_name}")
                return None
            listener = CodeCellListener(
                absolute_name=cell.component.AbsoluteName,
                code_name=code_name,
                cell_obj=cell.cell_obj.copy(),
                listeners=self,
            )
            self[code_name] = listener
            cell.component.addModifyListener(listener)
            return listener
        except Exception:
            self._log.exception(f"Error adding listener: {code_name}")
            return None

    def remove_all_listeners(self) -> None:
        """
        Remove all listeners from the current document.
        """
        self._log.debug("Removing all listeners")
        for listener in self.values():
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                cell.component.removeModifyListener(listener)
        self.clear()
        self._log.debug("Removed all listeners")

    def add_all_listeners(self) -> None:
        """
        Add all listeners to the current document.

        Calling this method will remove any existing Listeners before adding new ones.
        """
        self.remove_all_listeners()
        self._log.debug("Adding all listeners")
        self._add_all_listeners()
        self._log.debug("Added all listeners")

    def remove_listener(self, cell: CalcCell, code_name: str) -> None:
        """
        Removes a listener from a cell.

        Args:
            cell (CalcCell): The cell to remove the listener from.
            code_name (str): The code name of the listener to remove.
        """
        try:
            if code_name in self._listeners:
                listener = self._listeners[code_name]
                if not self.is_cell_deleted(cell.component):
                    cell.component.removeModifyListener(listener)
                    self._log.debug(f"Removed listener from cell with codename {code_name}.")
                else:
                    self._log.debug(f"Cell with codename {code_name} has been deleted. Not removing listener.")
                del self._listeners[code_name]
            else:
                self._log.error(f"Listener does not exists for cell with codename {code_name}.")
        except Exception:
            self._log.error(f"Error removing listener from cell with codename {code_name}.", exc_info=True)

    def is_cell_deleted(self, cell: SheetCell) -> bool:
        """Gets if a sheet cell has been deleted."""
        ci = CellInfo(cell)
        return ci.is_cell_deleted()
