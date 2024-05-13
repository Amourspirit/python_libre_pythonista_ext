from __future__ import annotations
import os
import signal
import subprocess

# import contextlib
from typing import TYPE_CHECKING
from pathlib import Path

# from ...input_output.proc import kill_proc

from .term import Term

# https://stackoverflow.com/questions/33414041/terminal-window-with-running-command


class MacTerminal(Term):
    """
    A class to represent a Gnome Terminal.
    """

    def __init__(self) -> None:
        """Initialize the Gnome Terminal."""
        super().__init__()
        ext_path = self.config.extension_info.get_extension_loc(self.config.lo_identifier)
        self._script_path = Path(ext_path) / "scripts"
        self._script_py = self._script_path / "mac_progress.py"

    def get_is_match(self) -> bool:
        """Check if matches for Mac"""
        return self.config.is_mac

    def start(self, msg: str = "Installing Package:", title: str = "Progress") -> None:
        """Start the terminal."""
        self._start_via_osascript(msg, title)

    def _start_via_osascript(self, msg: str, title: str) -> None:
        try:
            # https://stackoverflow.com/questions/2940916/how-do-i-embed-an-applescript-in-a-python-script
            script = f"""
            tell application "Terminal"
                do script "{self.config.python_path} '{self._script_py}' '{msg}'"
            end tell
            """
            # self.logger.debug(f"Start() script: {script}")
            subprocess.run(["osascript", "-e", script], capture_output=True)
        except Exception as err:
            self.logger.error(f"Error starting progress indicator: {err}")

    def stop(self) -> None:
        """Stop the terminal."""
        # When kill_command_line is called mac_progress.py will detect the SIGINT and exit it loop.
        self._kill_command_line()

    def _kill_command_line(self) -> None:
        # sourcery skip: extract-method

        try:
            cmd = "ps -ef | grep mac_progress.py | grep -v grep | awk '{print $2}'"
            ps_command = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            pid_str = ps_command.stdout.read()  # type: ignore
            ret_code = ps_command.wait()
            assert ret_code == 0, "ps command returned %d" % ret_code
            # os.kill(int(pid_str), signal.SIGTERM)
            os.kill(int(pid_str), signal.SIGINT)
        except Exception as err:
            self._logger.error(f"Error killing progress indicator: {err}")
            self._proc = None
