from __future__ import annotations
from ...config import Config
from ...oxt_logger import OxtLogger


class Term:
    """Base Terminal Class"""

    def __init__(self) -> None:
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)

    def get_code(self, msg: str) -> str:
        """Get the code to run in the terminal."""
        code = f"""
import time
print('{msg} ', flush=True, end='')
while True:
    print('.', flush=True, end='')
    time.sleep(1)
"""
        return code.strip()

    @property
    def config(self) -> Config:
        """Get the config."""
        return self._config

    @property
    def logger(self) -> OxtLogger:
        """Get the logger."""
        return self._logger
