from __future__ import annotations
from typing import Any, List
import subprocess
import os
import signal

from ...input_output import file_util
from .term import Term


class GnomeTerminal(Term):
    """
    A class to represent a Gnome Terminal.
    """

    def __init__(self) -> None:
        """Initialize the Gnome Terminal."""
        super().__init__()
        self._pid = -1

    def get_is_match(self) -> bool:
        """Check if matches for Linux Gnome Terminal."""
        if not self.config.is_linux:
            return False
        if self.config.is_app_image:
            return False
        if self.config.is_flatpak:
            return False
        if self.config.is_snap:
            return False
        return bool(file_util.which("gnome-terminal"))

    def _get_command(self, msg: str, title: str) -> List[str]:
        # https://stackoverflow.com/questions/34659433/terminate-a-gnome-terminal-opened-with-subprocess
        cmd = f'{self.config.python_path} -c "{self.get_code(msg)}"'
        return [
            "gnome-terminal",
            "--disable-factory",
            "--hide-menubar",
            f"--title={title}",
            "--",
            "sh",
            "-c",
            cmd,
        ]

    def start(self, msg: str, title: str = "Progress") -> None:
        """Start the terminal."""
        try:
            proc_cmd = self._get_command(msg, title)
            proc = subprocess.Popen(
                proc_cmd,
                shell=False,
                preexec_fn=os.setpgrp,  # type: ignore
            )
            self._pid = proc.pid
        except Exception as err:
            self.logger.error(f"Error starting progress indicator: {err}")
            self._pid = -1

    def stop(self) -> None:
        """Stop the terminal."""
        if self._pid == -1:
            self.logger.debug("No terminal to stop.")
            return
        try:
            os.killpg(self._pid, signal.SIGINT)  # type: ignore
        except Exception as err:
            self.logger.error(f"Error stopping progress indicator: {err}")
        self._pid = -1

    # def _kill_linux(self) -> None:
    #     # sourcery skip: extract-method

    #     try:
    #         cmd = 'ps -ef | grep "import time print(\'Installing:" | grep "sh -c" | grep -v grep | awk \'{print $2}\''
    #         ps_command = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #         pid_str = ps_command.stdout.read()  # type: ignore
    #         ret_code = ps_command.wait()
    #         assert ret_code == 0, "ps command returned %d" % ret_code
    #         os.kill(int(pid_str), signal.SIGTERM)
    #     except Exception as err:
    #         self._logger.error(f"Error killing progress indicator: {err}")
    #         self._proc = None
