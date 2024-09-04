from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    # just for design time
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class CallbackHolder:
    def __init__(self) -> None:
        # Initialize a dictionary to hold callbacks and their arguments
        self._callbacks = {}
        self._log = OxtLogger(log_name=self.__class__.__name__)

    def add(self, callback: Any, *args: Any, **kwargs: Any) -> None:
        # Store the callback along with its arguments
        # The callback function itself is the key, and its arguments are the value
        if self._log.is_debug:
            self._log.debug(f"Adding callback: {callback} with args: {args} and kwargs: {kwargs}")
        self._callbacks[callback] = (args, kwargs)

    def execute(self) -> None:
        # Iterate through the stored callbacks and their arguments, executing each one
        if not self._callbacks:
            self._log.debug("No callbacks to execute")
            return
        for callback, (args, kwargs) in self._callbacks.items():
            callback(*args, **kwargs)
