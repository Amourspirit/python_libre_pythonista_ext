"""
Manages breakpoints in the code. This is useful for debugging when the code is
running in a headless environment or in a extension environment where the debugger can be attached.

Example usage for BreakMgr:

.. code-block:: python

    from break_mgr import BreakMgr

    break_mgr = BreakMgr()

    # Set breakpoint at label 'critical_section'
    break_mgr.add_breakpoint('critical_section')

    def some_function():
        # Some code

        # Check for breakpoint at 'critical_section'
        break_mgr.check_breakpoint('critical_section')

        # Rest of your code

Example usage for check_breakpoint decorator:

.. code-block:: python

    from break_mgr import BreakMgr, check_breakpoint

    # Initialize the breakpoint manager
    break_mgr = BreakMgr()

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
from functools import wraps

if TYPE_CHECKING:
    import debugpy  # type: ignore # noqa: F401
else:
    try:
        import debugpy  # type: ignore # noqa: F401
    except (ModuleNotFoundError, ImportError):
        print("debugpy not found")
        debugpy = None


class BreakMgr:
    """Breakpoint Manager"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BreakMgr, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_is_init"):
            if debugpy is not None:
                self._debug_attached = os.getenv("LIBREOFFICE_DEBUG_ATTACHED") == "1"
            return

        self.breakpoints: Set[str] = set()
        if debugpy is None:
            self._debug_attached = False
        else:
            self._debug_attached = os.getenv("LIBREOFFICE_DEBUG_ATTACHED") == "1"
        self._is_init = True

    def add_breakpoint(self, label: str):
        """
        Adds a breakpoint with the given label to the set of breakpoints.

        Args:
            label (str): The label for the breakpoint to be added.
        """
        self.breakpoints.add(label)

    def remove_breakpoint(self, label: str):
        """
        Removes a breakpoint with the given label.

        Args:
            label (str): The label of the breakpoint to be removed.
        """
        self.breakpoints.discard(label)

    def has_breakpoint(self, label: str) -> bool:
        """
        Check if a breakpoint with the given label exists.

        Args:
            label (str): The label of the breakpoint to check.

        Returns:
            bool: True if the breakpoint exists, False otherwise.
        """
        return label in self.breakpoints

    def clear_breakpoints(self):
        """
        Clears all breakpoints.
        This method removes all breakpoints from the internal breakpoint list.
        """
        self.breakpoints.clear()

    def check_breakpoint(self, label: str):
        """
        Checks if a breakpoint is set at the given label and triggers the debugger if it is.

        Args:
            label (str): The label to check for a breakpoint.

        Returns:
            None
        """
        if self._debug_attached and label in self.breakpoints:
            print(f"Breakpoint at label: {label}")
            # breakpoint()
            debugpy.breakpoint()  # type: ignore # noqa: F821

    @property
    def debugger_attached(self):
        """
        Check if the debugger is attached.
        Returns:
            bool: True if the debugger is attached, False otherwise.
        """

        return self._debug_attached


def check_breakpoint(label: str):
    """
    A decorator to check for breakpoints before executing the decorated function.

    Args:
        label (str): The label of the breakpoint to check.

    Returns:
        function: The decorated function with breakpoint checking.

    The decorator initializes an instance of ``BreakMgr`` and checks if a debugger is attached.
    If a debugger is attached, it prints a message indicating the label of the breakpoint being checked
    and calls the ``check_breakpoint`` method of ``BreakMgr`` with the provided label.
    If no debugger is attached, it simply executes the original function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            break_mgr = BreakMgr()
            if not break_mgr.debugger_attached:
                return func(*args, **kwargs)
            print(f"Checking breakpoint at label: {label}")
            break_mgr.check_breakpoint(label)
            return func(*args, **kwargs)

        return wrapper

    return decorator
