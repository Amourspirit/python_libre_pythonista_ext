from __future__ import annotations
from typing import Dict, TYPE_CHECKING, Iterator
from ooodev.loader import Lo
from .callback_holder import CallbackHolder
from ..utils.singleton_base import SingletonBase
from ..ex import RuntimeUidError

if TYPE_CHECKING:
    # just for design time
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class SharedCb(SingletonBase):
    """
    A singleton class that holds a dictionary of CallbackHolder objects.

    This class provides a way to share CallbackHolder objects between different parts of the code.
    For example it makes it possible to set callbacks in OnDocumentLoad and run them one time in OnDocumentFocus.
    This gives a way to delay the execution of a callback until a certain event occurs.

    .. code-block:: python

        # in focus_job.py
        sc = SharedCb()
        if CB_DOC_FOCUS_GAINED in sc:
            sc.execute(CB_DOC_FOCUS_GAINED)
    """

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        self.runtime_uid: str
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Init")
        self._held: Dict[str, CallbackHolder] = {}
        # self._doc = doc
        self._is_init = True

    def __delitem__(self, name: str) -> None:
        del self._held[name]

    def __getitem__(self, name: str) -> CallbackHolder:
        return self._held[name]

    def __setitem__(self, name: str, cbh: CallbackHolder) -> None:
        self.add(name, cbh)

    def __contains__(self, name: str) -> bool:
        return name in self._held

    def __iter__(self) -> Iterator[str]:
        return iter(self._held)

    def _check_runtime_uid(self) -> bool:
        with self._log.indent(True):
            try:
                if Lo.current_doc.runtime_uid == self.runtime_uid:  # type: ignore
                    return True
                else:
                    self._log.error(
                        f"Runtime UID mismatch. Current: {Lo.current_doc.runtime_uid}, SharedCb: {self.runtime_uid}"  # type: ignore
                    )
                    return False
            except Exception:
                self._log.exception("_check_runtime_uid() Error getting current document")
                return False

    def add(self, name: str, cbh: CallbackHolder) -> None:
        """Add a CallbackHolder with the given name. If the name already exists, raise a ValueError."""
        with self._log.indent(True):
            if not self._check_runtime_uid():
                return None
            if name in self._held:
                self._log.error(f"CallbackHolder with name '{name}' already exists")
                raise ValueError(f"CallbackHolder with name '{name}' already exists")

            self._held[name] = cbh
            self._log.debug(f"Added CallbackHolder with name '{name}'")

    def update(self, name: str, cbh: CallbackHolder) -> None:
        """Update the CallbackHolder with the given name. If the name does not exist, add it."""
        with self._log.indent(True):
            if not self._check_runtime_uid():
                return None
            if name in self._held:
                self._log.debug(f"Updating CallbackHolder with name '{name}'")
                self._held[name] = cbh
            else:
                self.add(name, cbh)

    def add_callback(self, name: str, callback, *args, **kwargs) -> CallbackHolder:  # noqa: ANN001, ANN002, ANN003
        """
        Add a callback to a CallbackHolder with the given name. If the name does not exist, raise a KeyError.

        Args:
            name (str): callback holder name
            callback (function): callback function

        Raises:
            RuntimeUidError: If the runtime UID does not match ( incorrect document ).

        Returns:
            CallbackHolder: CallbackHolder object
        """
        with self._log.indent(True):
            if not self._check_runtime_uid():
                raise RuntimeUidError("Runtime UID mismatch")
            cbh = CallbackHolder()
            cbh.add(callback, *args, **kwargs)
            self.add(name, cbh)
            return cbh

    def remove(self, name: str) -> None:
        """Remove the CallbackHolder with the given name. If the name does not exist, raise a KeyError."""
        with self._log.indent(True):
            if not self._check_runtime_uid():
                return None
            try:
                del self[name]
                self._log.debug(f"Removed CallbackHolder with name '{name}'")
            except KeyError:
                self._log.error(f"CallbackHolder with name '{name}' does not exist")
                raise KeyError(f"CallbackHolder with name '{name}' does not exist")

    def execute(self, name: str, remove: bool = True) -> None:
        """
        Execute the CallbackHolder with the given name. If the name does not exist, Log error entry is created.

        Args:
            name (str): Name of the CallbackHolder to execute
            remove (bool, optional): Specifies if the callback should be removed after it is called. Defaults to True.

        Returns:
            None:
        """
        with self._log.indent(True):
            if not name in self._held:
                self._log.error(f"CallbackHolder with name '{name}' does not exist")
                return None
            if not self._check_runtime_uid():
                return None
            try:
                self._log.debug(f"Executing CallbackHolder with name '{name}'")
                cbh = self._held[name]
                cbh.execute()
                self._log.debug(f"Executed CallbackHolder with name '{name}'")
            except Exception:
                self._log.exception(f"Error executing CallbackHolder with name '{name}'")
            self._log.debug(f"Executed CallbackHolder with name '{name}'")
            if remove:
                self.remove(name)
            return None
