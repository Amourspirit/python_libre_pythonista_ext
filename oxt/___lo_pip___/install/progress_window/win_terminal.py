from __future__ import annotations
from typing import Any, List
import subprocess
from ...input_output.proc import kill_proc

from .term import Term


class WindowsTerminal(Term):
    """
    A class to represent a Gnome Terminal.
    """

    def __init__(self) -> None:
        """Initialize the Gnome Terminal."""
        super().__init__()
        self._pid = -1

    def get_is_match(self) -> bool:
        """Check if matches for Windows."""
        return self.config.is_win

    def _get_command(self, msg: str, title: str) -> List[str]:
        """Get the list of versions."""
        return [str(self.config.python_path), "-c", self.get_code(msg)]

    def start(self, msg: str, title: str = "Progress") -> None:
        """Start the terminal."""
        try:
            proc_cmd = self._get_command(msg, title)
            proc = proc = subprocess.Popen(
                proc_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
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
            kill_proc(self._pid)
        except Exception as err:
            self.logger.error(f"Error stopping progress indicator: {err}")
        self._pid = -1
