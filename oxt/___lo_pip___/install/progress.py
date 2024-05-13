from __future__ import annotations
from typing import TYPE_CHECKING
import subprocess
import os
import signal

from ..oxt_logger import OxtLogger
from .progress_window.progress_rules import ProgressRules
from ..config import Config


class Progress:
    def __init__(self, start_msg: str, title: str = "Terminal"):
        self._start_msg = start_msg
        self._title = title
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)
        rules = ProgressRules()
        self._progress_obj = rules.get_progress()

    def start(self) -> None:
        """Start the progress indicator as a terminal window."""
        if self._progress_obj is None:
            self._logger.debug("No terminal found. Progress indicator will not be shown.")
            return
        self._progress_obj.start(msg=self._start_msg, title=self._title)

    def kill(self) -> None:
        if self._progress_obj:
            self._progress_obj.stop()

    def _kill_linux(self) -> None:
        # sourcery skip: extract-method

        try:
            cmd = 'ps -ef | grep "import time print(\'Installing:" | grep "sh -c" | grep -v grep | awk \'{print $2}\''
            ps_command = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            pid_str = ps_command.stdout.read()  # type: ignore
            ret_code = ps_command.wait()
            assert ret_code == 0, "ps command returned %d" % ret_code
            os.kill(int(pid_str), signal.SIGTERM)
        except Exception as err:
            self._logger.error(f"Error killing progress indicator: {err}")
            self._proc = None
