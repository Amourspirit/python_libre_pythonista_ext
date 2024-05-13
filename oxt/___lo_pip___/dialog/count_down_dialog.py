from __future__ import annotations
from typing import Any
import time
import threading
import uno

from .temp_dialog import TempDialog
from ..thread.runners import run_in_thread
from ..config import Config


class CountDownDialog:
    """Displays a count down dialog."""

    def __init__(self, msg: str, title: str = "INFO", display_time: int = 3, ctx: Any = None) -> None:
        self._is_stopped = False
        self._lock = threading.Lock()
        self._msg = msg
        self._title = title
        self._display_time = display_time
        self._ctx = ctx

    def start(self) -> None:
        """Start the progress."""

        @run_in_thread
        def show_some_progress(ctx, s_title: str, s_msg: str, display_time: int) -> None:
            # from ___lo_pip___.dialog.infinite_progress import InfiniteProgress
            count = display_time
            cfg = Config()
            prop_names = ["Closeable"]
            prop_values = [False]
            if cfg.dialog_desktop_owned:
                prop_names.append("DesktopAsParent")
                prop_values.append(True)
            tmp_dialog = TempDialog(
                ctx=ctx,
                title=s_title,
                msg=s_msg,
                prop_names=prop_names,
                prop_values=prop_values,
            )
            while True:
                with self._lock:
                    if self._is_stopped or count <= 0:
                        break
                count -= 1
                tmp_dialog.dialog.setVisible(True)
                tmp_dialog.update(f"{s_msg} ...{count}")
                time.sleep(1)
            tmp_dialog.dialog.dispose()

        ctx = self._ctx or uno.getComponentContext()
        show_some_progress(ctx, self._title, self._msg, self._display_time)

    def stop(self) -> None:
        """Stop the progress."""
        self._is_stopped = True
