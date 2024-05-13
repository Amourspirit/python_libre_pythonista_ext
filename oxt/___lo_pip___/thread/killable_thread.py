from __future__ import annotations
from typing import Any, Callable, Optional, Union
import sys
import threading


class KillableThread(threading.Thread):
    """
    A Thread that can be killed.

    Example:

        .. code-block:: python

            def run_in_thread(fn):
                def run(*k, **kw):
                    t = threading.Thread(target=fn, args=k, kwargs=kw)
                    t.start()
                    return t
                return run

            def log_runner(logger) -> None:
                while True:
                    logger.debug("running log_runner")
                    time.sleep(1)

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

            g_exportedScripts = (log_progress,)
    """

    # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
    def __init__(self, *args: Any, **keywords: Any) -> None:
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self) -> None:
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.global_trace)
        self.__run_backup()
        self.run = self.__run_backup

    def global_trace(self, frame: Any, event: str, arg: Any) -> Optional[Union[Callable, None]]:  # type: ignore[override] # pylint: disable=line-too-long
        return self.local_trace if event == "call" else None

    def local_trace(self, frame: Any, event: str, arg: Any) -> Optional[Union[Callable, None]]:
        if event == "line" and self.killed:
            raise SystemExit()
        return self.local_trace

    def kill(self) -> None:
        self.killed = True
