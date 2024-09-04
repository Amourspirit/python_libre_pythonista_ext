from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class LogInst(OxtLogger):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LogInst, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_init = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_is_init", False):
            return
        log_name = "___lo_pip___"
        super().__init__(log_name=log_name)
        self._is_init = True
