"""
Manages the code cells.
Updates caches when cell are modified, added, removed.
Manages adding and removing listeners to cells.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from ooodev.calc import CalcDoc
from .listen.code_cell_listener import CodeCellListener


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CellMgr:
    _instances = {}

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
        self._doc = doc
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug(f"init for doc: {doc.runtime_uid}")
        self._listeners = {}  # type: dict[str, CodeCellListener]
        self._is_init = True

    def add_listener(self, cell_name: str) -> None:
        """
        Add a listener to a cell.
        """
        if cell_name not in self._listeners:
            listener = CodeCellListener(cell_name)
            self._listeners[cell_name] = listener
            self._logger.debug(f"Added listener to cell: {cell_name}")
        else:
            self._logger.error(f"Listener already exists for cell: {cell_name}")

    def remove_listener(self, cell_name: str) -> None:
        """
        Remove a listener from a cell.
        """
        if cell_name in self._listeners:
            del self._listeners[cell_name]
            self._logger.debug(f"Removed listener from cell: {cell_name}")
        else:
            self._logger.error(f"Listener does not exist for cell: {cell_name}")

    def remove_all_listeners(self) -> None:
        """
        Remove all listeners.
        """
        self._listeners.clear()
        self._logger.debug("Removed all listeners")

    def get_listener(self, cell_name: str) -> CodeCellListener:
        """
        Get a listener for a cell.
        """
        listener = self._listeners.get(cell_name, None)
        if listener is None:
            self._logger.error(f"Listener does not exist for cell: {cell_name}")
            raise KeyError(f"Listener does not exist for cell: {cell_name}")
        return listener

    def has_listener(self, cell_name: str) -> bool:
        """
        Check if a listener exists for a cell.
        """
        return cell_name in self._listeners

    def get_all_listeners(self) -> dict[str, CodeCellListener]:
        """
        Get all listeners.
        """
        return self._listeners

    def __len__(self) -> int:
        return len(self._listeners)

    def __iter__(self):
        return iter(self._listeners)

    def __contains__(self, cell_name: str) -> bool:
        return cell_name in self._listeners

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
            del cls._instances[key]
