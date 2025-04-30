from __future__ import annotations
from typing import Any, cast, Dict, Generator, Iterator, Iterable, TYPE_CHECKING
from contextlib import contextmanager

from ooodev.calc import CalcDoc, CalcCell, CellObj


if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell  # service
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listener import CodeCellListener
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listener import CodeCellListener
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


_KEY = "libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners.CodeCellListeners"


# NOTE:
# When removeModifyListener is called it seems the listener is not always removed.
# This can be a major issue when a py cell is being deleted.
# It may cause a recursive loop.
# The fix is to make certain the listener is disabled by calling listener.set_trigger_state(False)
# At least this way if the listener is not removed it will not trigger any events.


class CodeCellListeners(LogMixin):
    """
    Singleton Class. Manages cell listeners for a LibreOffice Calc document.

    This class tracks and manages CodeCellListener instances for cells in a Calc document.
    It provides methods to add, remove, and access listeners by their code names.

    Attributes:
        _doc (CalcDoc): The Calc document being monitored
        _qry_handler: Query handler for executing queries
        _listeners (Dict[str, CodeCellListener]): Dictionary mapping code names to listeners
    """

    def __new__(cls, doc: CalcDoc) -> CodeCellListeners:
        gbl_cache = DocGlobals.get_current(doc.runtime_uid)
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: CalcDoc) -> None:
        """
        Initialize a new CodeCellListeners instance.

        Args:
            doc (CalcDoc): The Calc document to monitor
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._doc = doc
        self._qry_handler = QryHandlerFactory.get_qry_handler()
        self._listeners: Dict[str, CodeCellListener] = {}
        self.log.debug("Init")
        self._is_init = True

    def __contains__(self, key: str) -> bool:
        """Check if a listener exists for the given code name."""
        return key in self._listeners

    def __getitem__(self, key: str) -> CodeCellListener:
        """Get a listener by its code name."""
        return self._listeners[key]

    def __setitem__(self, key: str, value: CodeCellListener) -> None:
        """
        Set a listener for a code name. Adds the listener to the cell and stores it.

        Args:
            key (str): Code name for the listener
            value (CodeCellListener): Listener instance to add
        """
        try:
            cell = self._get_calc_cell(value.cell_obj)
            if cell is not None:
                # attempt to remove the listener just in case it has been added.
                cell.component.removeModifyListener(value)
                cell.component.addModifyListener(value)
                self._listeners[key] = value
            else:
                self.log.error("Cell not found: %s", value.cell_obj)

        except Exception:
            self.log.exception("Error setting listener: %s", key, exc_info=True)

    def __delitem__(self, key: str) -> None:
        """
        Remove a listener by its code name.

        Args:
            key (str): Code name of the listener to remove
        """
        try:
            if not key in self:
                self.log.error("Key not found: %s", key)
                return
            listener = self._listeners[key]
            listener.set_trigger_state(False)
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                cell.component.removeModifyListener(listener)
            else:
                self.log.error("Cell not found: %s", listener.cell_obj)

            del self._listeners[key]
        except Exception:
            self.log.exception("Error deleting listener: %s", key, exc_info=True)

    def __iter__(self) -> Iterator[str]:
        """Iterator over listener code names."""
        return iter(self._listeners)

    def __len__(self) -> int:
        """Get the number of active listeners."""
        return len(self._listeners)

    def __str__(self) -> str:
        """String representation of the instance."""
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        """Detailed string representation of the instance."""
        return f"<{self.__class__.__name__}()>"

    def items(self) -> Iterable[tuple[str, CodeCellListener]]:
        """Get all code name-listener pairs."""
        return self._listeners.items()

    def keys(self) -> Iterable[str]:
        """Get all listener code names."""
        return self._listeners.keys()

    def values(self) -> Iterable[CodeCellListener]:
        """Get all listener instances."""
        return self._listeners.values()

    def clear(self) -> None:
        """Remove all listeners from the internal dictionary."""
        with self.log.indent(True):
            self.log.debug("Clearing all listeners")
            self._listeners.clear()

    def _get_calc_cell(self, cell_obj: CellObj) -> CalcCell | None:
        """
        Get a CalcCell instance for a given CellObj.

        Args:
            cell_obj (CellObj): Cell object to look up

        Returns:
            CalcCell | None: The found cell or None if invalid/not found
        """
        if cell_obj.sheet_idx < 0:
            self.log.error("Invalid sheet index: %s", cell_obj.sheet_idx)
            return None
        doc = cast(CalcDoc, self._doc)
        sheet = doc.sheets[cell_obj.sheet_idx]
        return sheet[cell_obj]

    def qry_code_name(self, calc_cell: CalcCell) -> Result[str, None] | Result[None, Exception]:
        """
        Query the code name for a cell.

        Args:
            calc_cell (CalcCell): Cell to query

        Returns:
            str: The cell's code name
        """
        qry = QryCodeName(cell=calc_cell)
        return self._qry_handler.handle(qry)

    def get_cell_listener(self, cell_obj: CellObj) -> Result[CodeCellListener, None] | Result[None, Exception]:
        """
        Get the listener for a specific cell.

        Args:
            cell_obj (CellObj): Cell to get the listener for

        Returns:
            CodeCellListener | None: The cell's listener or None if not found
        """
        cell = self._get_calc_cell(cell_obj)
        if cell is None:
            self.log.warning("Cell not found: %s. Returning None", cell_obj)
            return Result.failure(Exception("Cell not found"))
        code_name_qry = self.qry_code_name(cell)
        if Result.is_failure(code_name_qry):
            self.log.warning("Cell has no code name: %s.", cell_obj)
            return code_name_qry
        code_name = code_name_qry.data
        if code_name not in self:
            self.log.warning("Cell listener not found: %s. Returning None", code_name)
            return Result.failure(Exception("Cell listener not found"))
        return Result.success(self[code_name])

    def get(self, code_name: str) -> Result[CodeCellListener, None] | Result[None, Exception]:
        """
        Get a listener by its code name.

        Args:
            code_name (str): Code name to look up

        Returns:
            CodeCellListener | None: The listener or None if not found
        """
        if code_name in self:
            return Result.success(self[code_name])
        self.log.warning("Listener not found: %s", code_name)
        return Result.failure(Exception("Listener not found"))

    def pop(self, code_name: str) -> Result[CodeCellListener, None] | Result[None, Exception]:
        """
        Remove and return a listener by its code name.

        Args:
            code_name (str): Code name of the listener to remove

        Returns:
            CodeCellListener | None: The removed listener or None if not found
        """
        if code_name in self:
            listener = self[code_name]
            listener.set_trigger_state(False)
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                cell.component.removeModifyListener(listener)
            else:
                self.log.error("Cell not found: %s", listener.cell_obj)

            del self._listeners[code_name]
            return Result.success(listener)
        self.log.warning("Listener not found: %s", code_name)
        return Result.failure(Exception("Listener not found"))

    def add_listener(self, cell: CalcCell) -> Result[CodeCellListener, None] | Result[None, Exception]:
        """
        Add a new listener to a cell.

        Args:
            cell (CalcCell): Cell to add the listener to

        Returns:
            Result[CodeCellListener, None] | Result[None, Exception]: The created listener or None if failed
        """
        code_name_qry = self.qry_code_name(cell)
        if Result.is_failure(code_name_qry):
            self.log.warning("Cell has no code name: %s", cell.cell_obj)
            return code_name_qry
        code_name = code_name_qry.data
        try:
            if code_name in self:
                self.log.debug("Listener already exists: %s", code_name)
                return Result.failure(Exception("Listener already exists"))
            listener = CodeCellListener(
                absolute_name=cell.component.AbsoluteName,
                code_name=code_name,
                cell_obj=cell.cell_obj.copy(),
                listeners=self,
            )
            self[code_name] = listener
            cell.component.addModifyListener(listener)
            result = Result.success(listener)
            self.log.debug("Added listener for cell %s with codename: %s", cell.cell_obj, code_name)
            return result
        except Exception:
            self.log.exception("Error adding listener for cell %s with codename: %s", cell.cell_obj, code_name)
            return Result.failure(Exception("Error adding listener"))

    def remove_all_listeners(self) -> None:
        """Remove all listeners from their cells and clear the internal dictionary."""
        self.log.debug("Removing all listeners")
        for listener in self.values():
            cell = self._get_calc_cell(listener.cell_obj)
            if cell is not None:
                listener.set_trigger_state(False)
                cell.component.removeModifyListener(listener)
        self.clear()
        self.log.debug("Removed all listeners")

    def remove_listener(self, cell: CalcCell) -> bool:
        """
        Remove a specific listener from a cell.

        Args:
            cell (CalcCell): Cell to remove the listener from

        Returns:
            bool: True if the listener was removed, False otherwise
        """
        code_name = ""
        try:
            code_name_result = self.qry_code_name(cell)
            if Result.is_failure(code_name_result):
                return False
            code_name = code_name_result.data

            if code_name in self._listeners:
                listener = self._listeners[code_name]
                listener.set_trigger_state(False)
                if not self.is_cell_deleted(cell.component):
                    cell.component.removeModifyListener(listener)
                    self.log.debug("Removed listener from cell with codename %s.", code_name)
                else:
                    self.log.debug("Cell with codename %s has been deleted. Not removing listener.", code_name)
                del self._listeners[code_name]
                return True
            else:
                self.log.warning("Listener does not exists for cell with codename %s.", code_name)
                return False
        except Exception:
            self.log.exception("Error removing listener from cell %s with codename %s.", cell.cell_obj, code_name)
        return False

    def is_cell_deleted(self, cell: SheetCell) -> bool:
        """
        Check if a cell has been deleted.

        Args:
            cell (SheetCell): Cell to check

        Returns:
            bool: True if the cell has been deleted, False otherwise
        """
        qry = QryCellIsDeleted(cell=cell)
        return self._qry_handler.handle(qry)

    @contextmanager
    def suspend_listener_ctx(self, cell: CalcCell) -> Generator[None, Any, None]:
        """
        Context manager that on entry suspends the listener for a cell if the listener exists.
        On exit the state is added back to the cell if it existed.
        """

        self.log.debug("Suspend listener context for cell: %s", cell.cell_obj)
        listener = None
        code_name_result = self.qry_code_name(cell)
        if Result.is_failure(code_name_result):
            self.log.warning("Cell has no code name: %s", cell.cell_obj)
            return
        code_name = code_name_result.data

        trigger_state = False
        try:
            if code_name in self._listeners:
                self.log.debug("suspending listeners for cell: %s", cell.cell_obj)
                listener = self._listeners[code_name]
                trigger_state = listener.get_trigger_state()
                listener.set_trigger_state(False)
            else:
                self.log.debug("Listener does not exist for cell: %s", cell.cell_obj)
            yield
        finally:
            if listener is not None:
                if trigger_state:
                    self.log.debug("Resuming listeners for cell: %s", cell.cell_obj)
                    listener.set_trigger_state(True)
                    self._listeners[code_name] = listener
                else:
                    self.log.debug("Not resuming listeners for cell: %s", cell.cell_obj)
