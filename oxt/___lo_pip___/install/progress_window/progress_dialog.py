from __future__ import annotations
import time
import threading
import uno

from ...dialog.infinite_progress import InfiniteProgressDialog
from ...thread.runners import run_in_thread
from ...events.startup.startup_monitor import StartupMonitor


class ProgressDialog:
    """A progress dialog rule."""

    def __init__(self) -> None:
        """Initialize the progress dialog object."""
        self._is_stopped = False
        self._lock = threading.Lock()
        self._startup_monitor = StartupMonitor()

    def get_is_match(self) -> bool:
        """Check if the terminal is a match"""
        # if window has started then a progress dialog can be shown.
        return self._startup_monitor.window_started

    def start(self, msg: str, title: str = "Progress") -> None:
        """Start the terminal."""

        @run_in_thread
        def show_some_progress(ctx, s_title: str, s_msg: str) -> None:
            # from ___lo_pip___.dialog.infinite_progress import InfiniteProgress
            ellipsis = 0
            in_progress = InfiniteProgressDialog(ctx, title=s_title, msg=s_msg)
            while True:
                with self._lock:
                    if self._is_stopped:
                        break
                ellipsis += 1
                in_progress.dialog.setVisible(True)
                in_progress.update(f"{s_msg} {'.' * ellipsis}")
                if ellipsis == 300:
                    ellipsis = 0
                time.sleep(1)
            in_progress.dialog.dispose()

        show_some_progress(uno.getComponentContext(), title, msg)

    def stop(self) -> None:
        """Stop the terminal."""
        self._is_stopped = True
