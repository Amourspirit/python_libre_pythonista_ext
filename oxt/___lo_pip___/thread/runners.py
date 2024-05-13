from __future__ import annotations
import threading
from typing import Any, Callable


def run_in_thread(fn: Callable[..., Any]) -> Callable[..., threading.Thread]:
    """
    Decorator method to run a function in a thread.

    Args:
        fn (Callable[..., Any]): Function to run in a thread.

    Returns:
        Callable[..., threading.Thread]: _description_

    Example:

        .. code-block:: python

            @run_in_thread
            def actual_log_progress() -> None:
                logger = OxtLogger(log_name=__name__)
                logger.debug("Log_progress: Start")
                my_progress = KillableThread(target=log_runner, args=(logger,))
                my_progress.start()
                logger.debug("Log_progress: Started")
                time.sleep(10)
                my_progress.kill()
                my_progress.join()
                logger.debug("Log_progress: Done")


            def log_progress(*args) -> None:
                actual_log_progress()

    """

    # https://wiki.documentfoundation.org/Macros/Python_Guide/Useful_functions
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t

    return run
