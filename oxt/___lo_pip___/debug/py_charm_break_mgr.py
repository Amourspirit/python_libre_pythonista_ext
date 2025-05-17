"""
Manages breakpoints in the code. This is useful for debugging when the code is
running in a headless environment or in a extension environment where the debugger can be attached.

Example usage for PyCharmBreakMgr:

.. code-block:: python

    from break_mgr import PyCharmBreakMgr

    break_mgr = PyCharmBreakMgr()

    # Set breakpoint at label 'critical_section'
    break_mgr.add_breakpoint('critical_section')

    def some_function():
        # Some code

        # Check for breakpoint at 'critical_section'
        break_mgr.check_breakpoint('critical_section')

        # Rest of your code

Example usage for check_breakpoint decorator:

.. code-block:: python

    from break_mgr import PyCharmBreakMgr, check_breakpoint

    # Initialize the breakpoint manager
    break_mgr = PyCharmBreakMgr()

    # Add breakpoint labels
    break_mgr.add_breakpoint('init')
    break_mgr.add_breakpoint('process_data')

    @check_breakpoint('init')
    def initialize():
        # Initialization code
        print("Initializing...")
        # ...

    @check_breakpoint('process_data')
    def process_data():
        # Data processing code
        print("Processing data...")
        # ...

    def main():
        initialize()
        process_data()
        # ...

    if __name__ == '__main__':
        main()
"""

from __future__ import annotations
from typing import Set, TYPE_CHECKING
import os
import time
from functools import wraps

if TYPE_CHECKING:
    from oxt.___lo_pip___.lo_util.uno_context_mgr import uno_suspend_import
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    uno_suspend_import = None
    from libre_pythonista_lib.log.log_mixin import LogMixin

    try:
        from ___lo_pip___.lo_util.uno_context_mgr import uno_suspend_import
    except (ModuleNotFoundError, ImportError):
        print("uno_suspend_import not found")
        uno_suspend_import = None


class PyCharmBreakMgr(LogMixin):
    """Breakpoint Manager. Singleton Class."""

    _instance = None

    def __new__(cls, *args, **kwargs):  # noqa: ANN002, ANN003, ANN204
        if not cls._instance:
            cls._instance = super(PyCharmBreakMgr, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_init = False
        return cls._instance

    def __init__(self) -> None:
        if self._is_init:
            return
        LogMixin.__init__(self)
        self._debug_port = 6789
        self._host = "127.0.0.1"
        self.breakpoints: Set[str] = set()
        if not self.debugger_attached:
            self._init_debug()
        self.log.debug("PyCharmBreakMgr init")
        self._is_init = True

    def _init_debug(self) -> None:
        self.log.debug("_init_debug()")
        try:
            if os.getenv("ENABLE_LIBREOFFICE_DEBUG_PY_CHARM"):
                self._trace()
            else:
                self.log.debug("Debugging is disabled")

        except Exception:
            self.log.exception("Error attaching debugger")
            return

    def _trace(self) -> None:
        with uno_suspend_import():
            import pydevd_pycharm  # type: ignore
        os.environ["LIBREOFFICE_PY_CHARM_DEBUG_ATTACHED"] = "0"
        if self._debug_port > 0:
            pydevd_pycharm.stoptrace()
            self.log.debug("Debugger detached.")
            print(f"Waiting for debugger attach on port  {self._debug_port}")
            self.log.debug("Waiting for debugger attach on port %i ...", self._debug_port)
            time.sleep(1)
            pydevd_pycharm.settrace(
                host=self._host, port=self._debug_port, stdoutToServer=True, stderrToServer=True, suspend=False
            )
            os.environ["LIBREOFFICE_PY_CHARM_DEBUG_ATTACHED"] = "1"
            self.log.debug("Debugger attached.")
        else:
            self.log.warning("Debug port must be greater then 0")
            return

    def add_breakpoint(self, label: str) -> None:
        """
        Adds a breakpoint with the given label to the set of breakpoints.

        Args:
            label (str): The label for the breakpoint to be added.
        """
        self.breakpoints.add(label)
        self.log.debug(f"Added breakpoint for label: {label}")

    def remove_breakpoint(self, label: str) -> None:
        """
        Removes a breakpoint with the given label.

        Args:
            label (str): The label of the breakpoint to be removed.
        """
        self.breakpoints.discard(label)
        self.log.debug(f"Removed breakpoint for label: {label}")

    def has_breakpoint(self, label: str) -> bool:
        """
        Check if a breakpoint with the given label exists.

        Args:
            label (str): The label of the breakpoint to check.

        Returns:
            bool: True if the breakpoint exists, False otherwise.
        """
        return label in self.breakpoints

    def clear_breakpoints(self) -> None:
        """
        Clears all breakpoints.
        This method removes all breakpoints from the internal breakpoint list.
        """
        self.breakpoints.clear()
        self.log.debug("Cleared all breakpoints")

    def check_breakpoint(self, label: str) -> None:
        """
        Checks if a breakpoint is set at the given label and triggers the debugger if it is.

        Args:
            label (str): The label to check for a breakpoint.

        Returns:
            None
        """
        if not self.debugger_attached:
            self.log.debug("No debugger attached! Ignoring label: %s", label)
            return
        if label in self.breakpoints:
            self.log.debug("Breakpoint hit for label: %s", label)
            self._trace()
            breakpoint()
        else:
            self.log.debug("No breakpoint set for label: %s", label)

    @property
    def debugger_attached(self) -> bool:
        """
        Check if the debugger is attached.
        Returns:
            bool: True if the debugger is attached, False otherwise.
        """
        return os.getenv("LIBREOFFICE_PY_CHARM_DEBUG_ATTACHED") == "1"


def check_breakpoint(label: str):  # noqa: ANN201
    """
    A decorator to check for breakpoints before executing the decorated function.

    Args:
        label (str): The label of the breakpoint to check.

    Returns:
        function: The decorated function with breakpoint checking.

    The decorator initializes an instance of ``PyCharmBreakMgr`` and checks if a debugger is attached.
    If a debugger is attached, it prints a message indicating the label of the breakpoint being checked
    and calls the ``check_breakpoint`` method of ``PyCharmBreakMgr`` with the provided label.
    If no debugger is attached, it simply executes the original function.
    """

    def decorator(func):  # noqa: ANN001, ANN202
        @wraps(func)
        def wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            break_mgr = PyCharmBreakMgr()
            if not break_mgr.debugger_attached:
                return func(*args, **kwargs)
            # print(f"Checking breakpoint at label: {label}")
            break_mgr.check_breakpoint(label)
            return func(*args, **kwargs)

        return wrapper

    return decorator
