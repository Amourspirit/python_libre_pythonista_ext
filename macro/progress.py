"""
Example progress indicators.

This macro will only work if extension is installed.
"""
from __future__ import annotations
from typing import Any
import time
import threading
import uno

# rename lo_pip to the name you used in [tool.oxt.token]
# default is: lo_pip = "lo_pip" to get macro working inf your template copy.
from lo_pip.oxt_logger import OxtLogger
from lo_pip.dialog.infinite_progress import InfiniteProgress
from lo_pip.dialog.infinite_progress import InfiniteProgressDialog
from lo_pip.thread.runners import run_in_thread

# https://wiki.documentfoundation.org/Macros/Python_Guide/Useful_functions


class InfiniteLogging(threading.Thread):
    """
    Infinite logging thread.
    """

    def __init__(self, ctx: Any, title: str = "Infinite Progress", msg: str = "Please wait"):
        super().__init__()
        self._ctx = ctx
        self._title = title
        self._msg = msg
        self._ellipsis = 0
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._logger = OxtLogger(log_name=__name__)

    def run(self):
        # use the setVisible method and not Execute.
        # This makes visible the dialog and makes it not modal.
        # in_progress.dialog.setVisible(True)
        # _ = in_progress.execute()
        while not self._stop_event.is_set():
            with self._lock:
                # possibly sleep and update a label to show progress
                self._ellipsis += 1
                self._logger.debug(f"{self._msg}{'.' * self._ellipsis}")
                if self._ellipsis > 10:
                    self._ellipsis = 0
                time.sleep(1)

    def stop(self):
        self._stop_event.set()


def log_runner() -> None:
    # my_progress = InfiniteProgress(ctx)
    logger = OxtLogger(log_name="log_runner2")
    logger.debug("log_runner2: Start")

    ellipsis = 0
    # XSCRIPTCONTEXT.getComponentContext()
    ctx = uno.getComponentContext()
    progress = InfiniteProgressDialog(ctx=ctx, title="Infinite Progress", msg="Please wait")
    logger.debug("log_runner2: created InfiniteProgress instance")
    while True:
        try:
            logger.debug("log_runner2: looping")
            ellipsis += 1
            progress.dialog.setVisible(True)
            logger.debug("log_runner2: Setting Visible")
            progress.update(f"{progress.msg}{'.' * ellipsis}")
            logger.debug("log_runner2: Updating message")
            if ellipsis > 10:
                ellipsis = 0
            time.sleep(1)
        except Exception as e:
            logger.exception(e, exc_info=True)
            break


@run_in_thread
def actual_log_via_infinite_logging() -> None:
    logger = OxtLogger(log_name="actual_log_via_infinite_logging")

    inf = InfiniteLogging(ctx=uno.getComponentContext(), title="Infinite Progress", msg="Please wait")
    logger.debug("InfiniteLogging created")
    inf.start()
    logger.debug("InfiniteLogging started")
    time.sleep(10)
    inf.stop()
    logger.debug("InfiniteLogging stopped")


def log_via_infinite_logging(*args) -> None:
    actual_log_via_infinite_logging()


@run_in_thread
def actual_progress_via_infinite_progress() -> None:
    logger = OxtLogger(log_name="actual_progress_via_infinite_progress")
    inf = InfiniteProgress(ctx=uno.getComponentContext(), title="Infinite Progress", msg="Please wait")
    logger.debug("InfiniteProgress created")
    inf.start()
    logger.debug("InfiniteProgress started")
    time.sleep(10)
    inf.stop()
    logger.debug("InfiniteProgress stopped")


def progress_via_infinite_progress(*args) -> None:
    actual_progress_via_infinite_progress()


g_exportedScripts = (log_via_infinite_logging, progress_via_infinite_progress)
