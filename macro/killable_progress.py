"""
Example KillableThread progress indicators.

This macro will only work if extension is installed.

Outputs to configured log file.
"""
from __future__ import annotations
import time

# rename lo_pip to the name you used in [tool.oxt.token]
# default is: lo_pip = "lo_pip" to get macro working inf your template copy.
from lo_pip.oxt_logger import OxtLogger
from lo_pip.thread.runners import run_in_thread
from lo_pip.thread.killable_thread import KillableThread


# https://wiki.documentfoundation.org/Macros/Python_Guide/Useful_functions


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
