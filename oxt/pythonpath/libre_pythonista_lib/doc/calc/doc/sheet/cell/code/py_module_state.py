from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING, Union
from collections import OrderedDict

from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.module_state_item import ModuleStateItem

_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state.PyModuleState"


class PyModuleState(LogMixin):
    """
    Manages the state history of a Python module, implementing a singleton pattern per module.
    Tracks changes and allows rollback to previous states.
    """

    def __new__(cls, mod: PyModuleT) -> PyModuleState:
        """
        Creates or returns an existing instance for the given module.
        Implements singleton pattern based on module ID.

        Args:
            mod: Python module instance to manage state for

        Returns:
            PyModuleState: New or existing instance
        """
        gbl_cache = DocGlobals.get_current()
        mod_id = id(mod)
        key = f"{_KEY}_{mod_id}"
        if key in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[key]

        inst = super().__new__(cls)
        inst.cache_key = key
        inst._is_init = False
        inst.runtime_uid = gbl_cache.runtime_uid

        gbl_cache.mem_cache[key] = inst
        return inst

    def __init__(self, mod: PyModuleT) -> None:
        """
        Initializes the module state manager.

        Args:
            mod: Python module instance to manage state for
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self.log.debug("Init")
        self.cache_key: str
        self._shared_event = SharedEvent()
        self._py_mod = mod
        self.runtime_uid: str
        self._state_history: OrderedDict[Tuple[int, int, int], ModuleStateItem] = OrderedDict()
        self._max_history_size = 250  # Configurable maximum history size.
        self._is_init = True

    def __bool__(self) -> bool:
        """Returns True if the state history is not empty."""
        return len(self._state_history) > 0

    def __getitem__(self, cell: CalcCell) -> ModuleStateItem:
        """Gets state history for a cell using dictionary syntax."""
        key = self.convert_cell_to_tuple(cell)
        return self._state_history[key]

    def __setitem__(self, cell: CalcCell, value: ModuleStateItem) -> None:
        """Sets state history for a cell using dictionary syntax."""
        key = self.convert_cell_to_tuple(cell)
        self._state_history[key] = value

    def __contains__(self, cell: CalcCell) -> bool:
        """Returns True if state history exists for the cell."""
        key = self.convert_cell_to_tuple(cell)
        return key in self._state_history

    def __len__(self) -> int:
        """Returns the number of states in history."""
        return len(self._state_history)

    def _remove_state_history_by_cell(self, cell: CalcCell) -> None:
        """
        Removes all state history entries for and after the given cell.

        Args:
            cell: Cell to remove history from
        """
        state_key = cell.unique_id
        if not state_key in self._state_history:
            self.log.debug("State key '%s' not found in history", state_key)
            return
        # remove all keys after the current key
        keys = list(self._state_history.keys())
        index = keys.index(state_key)
        for i in range(index, len(keys)):
            key = keys[i]
            del self._state_history[key]

    def convert_cell_obj_to_tuple(self, cell: CellObj) -> Tuple[int, int, int]:
        """
        Converts a cell object to a tuple of (sheet index, row, column).

        Args:
            cell (CellObj): Cell object.

        Returns:
            Tuple[int, int, int]: Tuple of (sheet index, row, column).
        """
        col = cell.col_obj.index
        row = cell.row - 1
        sheet_idx = cell.sheet_idx
        return (sheet_idx, row, col)

    def convert_tuple_to_cell_obj(self, cell: Tuple[int, int, int]) -> CellObj:
        """
        Converts a tuple of (sheet index, row, column) to a cell object.

        Args:
            cell (Tuple[int, int, int]): Tuple of (sheet index, column, row).

        Returns:
            CellObj: Cell object.
        """
        return CellObj.from_idx(col_idx=cell[1], row_idx=cell[2], sheet_idx=cell[0])

    def convert_cell_to_tuple(self, cell: CalcCell) -> Tuple[int, int, int]:
        """
        Converts a CalcCell to a tuple of (sheet index, row, column).

        Args:
            cell (CalcCell): CalcCell object.

        Returns:
            Tuple[int, int, int]: Tuple of (sheet index, row, column).
        """
        return self.convert_cell_obj_to_tuple(cell.cell_obj)

    def update_key(self, old_cell: CellObj, new_cell: CellObj) -> None:
        """
        Updates the key for a cell.

        Args:
            old_cell (CellObj): Old cell object.
            new_cell (CellObj): New cell object.
        """
        self.log.debug("update_key() - Updating key for cell %s to %s", old_cell, new_cell)
        old_key = self.convert_cell_obj_to_tuple(old_cell)
        new_key = self.convert_cell_obj_to_tuple(new_cell)
        if old_key not in self._state_history:
            self.log.warning("update_key() - Old key not found: %s", old_key)
            return

        old_data = self._state_history.pop(old_key)
        new_data = ModuleStateItem(cell_obj=new_cell.copy(), mod_dict=old_data.mod_dict.copy(), owner=self)
        self._state_history[new_key] = new_data
        self.log.debug("update_key() - Updated key for cell %s to %s", old_cell, new_cell)

    def update_with_result(self, cell: CalcCell, code: str = "") -> DotDict[Any]:
        """
        Updates module with new code and saves the resulting state.

        Args:
            cell: Cell associated with the update
            code: Python code to execute

        Returns:
            DotDict containing the execution result
        """
        result = self._py_mod.update_with_result(code)
        state_item = ModuleStateItem(cell_obj=cell.cell_obj, mod_dict=self._py_mod.copy_dict(), owner=self)
        state_item.dd_data.update(result)
        state_key = self.convert_cell_to_tuple(cell)
        self._state_history[state_key] = state_item
        popped = []
        while len(self._state_history) > self._max_history_size:
            popped.append(self._state_history.popitem(last=False))
        if popped:
            self.log.debug("Popped %s items from history", len(popped))
        return result

    def set_global_var(self, var_name: str, value: Any) -> None:  # noqa: ANN401
        """
        Sets a global variable in the module.

        Args:
            var_name: Name of the variable
            value: Value to set
        """
        self._py_mod.set_global_var(var_name, value)

    def reset_module(self) -> None:
        """Resets the module and clears all state history."""
        self._py_mod.reset_module()
        self._state_history.clear()

    def reset_to_cell(self, cell: CalcCell, code: str = "") -> Any:  # noqa: ANN401
        """
        Resets module state to a specific cell and optionally executes new code.

        Args:
            cell: Cell to reset to
            code: Optional Python code to execute after reset

        Returns:
            Result of code execution or None if cell not found
        """
        if not cell in self:
            self.log.debug("Cell %s not found in state.", cell.cell_obj)
            return None
        state_item = self[cell]
        result = self._py_mod.reset_to_dict(state_item.mod_dict.copy(), code)
        self._remove_state_history_by_cell(cell)
        return result

    def rollback_to_state(self, cell: CalcCell) -> bool:
        """
        Rolls back the module to a previously saved state.

        Args:
            cell: Cell to rollback to

        Returns:
            bool: True if rollback successful, False if state not found
        """
        state_key = cell.unique_id
        if state_key not in self._state_history:
            self.log.debug("State key '%s' not found in history", state_key)
            return False

        state_item = self[cell]
        _ = self._py_mod.reset_to_dict(state_item.mod_dict.copy())
        self._remove_state_history_by_cell(cell)
        return True

    def get_last_item(self) -> Union[ModuleStateItem, None]:
        """Returns the last item in the state history or None if empty."""
        # See: cq.qry.calc.sheet.cell.state.qry_module_state_last_item.QryModuleStateLastItem
        if not self._state_history:
            return None
        last_key = list(self._state_history.keys())[-1]
        return self._state_history[last_key]

    # region Cache
    def clear_instance_cache(self) -> None:
        """
        Clears the instance cache.
        """
        gbl_cache = DocGlobals.get_current()

        if self.cache_key in gbl_cache.mem_cache:
            del gbl_cache.mem_cache[self.cache_key]
            self.log.debug("clear_instance_cache() - Cleared instance cache.")

    # endregion Cache

    @property
    def mod(self) -> PyModuleT:
        """Returns the managed Python module."""
        return self._py_mod
