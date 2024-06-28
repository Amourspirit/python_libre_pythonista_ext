from __future__ import annotations
from typing import Any, TYPE_CHECKING
import uno
from threading import Thread

from ooodev.events.args.event_args import EventArgs

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext
    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.dialog.py.dialog_mb import DialogMb

    XSCRIPTCONTEXT: XScriptContext

else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.dialog.py.dialog_mb import DialogMb


# Global dictionary to hold threads
threads_dict = {}
active_windows = {}


def thread_wrapper(ctx, inst_id, original_func):
    """
    Wrapper function to execute the original thread function and remove the thread from the dictionary upon completion.
    """
    global threads_dict
    try:
        original_func(ctx, inst_id)
    finally:
        # Remove the thread from the dictionary
        del threads_dict[inst_id]
        if inst_id in active_windows:
            del active_windows[inst_id]


def show_win_mb_thread(ctx, inst_id: str):
    """
    Handle the button action event.
    """
    global active_windows
    if inst_id in active_windows:
        del active_windows[inst_id]

    log = LogInst()
    log.debug("show_win_mb_thread debug")
    try:
        if DialogMb.has_instance(inst_id):
            mb = DialogMb.get_instance(inst_id)
        else:
            mb = DialogMb(ctx, inst_id)
            mb.text = "Hello, World!"
            mb.info = "Yes"
            # try:
            #     mb._frame.Title = "Hello, World!"
            # except Exception:
            #     log.error("show_win_mb_thread: Error", exc_info=True)
        active_windows[inst_id] = mb
        if mb.show():
            log.debug("show_win_mb_thread: OK")
            log.debug(f"show_win_mb_thread Text: {mb.text}")
        else:
            log.debug("show_win_mb_thread: Cancel")
        # mb.set_focus()
        mb.dispose()
    except Exception:
        log.error("show_win_mb_thread: Error", exc_info=True)


def dialog_mb_ok(src: Any, event: EventArgs):
    """
    Handle the button action event.
    """

    log = LogInst()
    log.debug("dialog_mb_ok debug")
    try:
        log.debug(f"dialog_mb_ok: {event.event_data.text}")
    except Exception:
        log.error("dialog_mb_ok: Error", exc_info=True)


def show_win_mb(*args):
    """
    Handle the button action event.
    """

    log = LogInst()
    log.debug("show_win_mb debug")
    try:
        ctx = XSCRIPTCONTEXT.getComponentContext()
        inst_id = "test"
        # Check if a thread with the same inst_id already exists
        if inst_id in active_windows:
            log.debug(f"Thread with inst_id '{inst_id}' is already running. Setting Focus")
            active_windows[inst_id].set_focus()
            return
        if inst_id not in threads_dict:
            # Wrap the original function
            target_func = lambda: thread_wrapper(ctx, inst_id, show_win_mb_thread)
            t = Thread(target=target_func)

            # Add the thread to the dictionary
            threads_dict[inst_id] = t

            t.start()
        else:
            log.debug(f"Thread with inst_id '{inst_id}' is already running.")

    except Exception:
        log.error("show_win_mb: Error", exc_info=True)
