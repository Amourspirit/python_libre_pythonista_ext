from typing import Any, cast, TYPE_CHECKING
from pathlib import Path
from ooodev.loader import Lo
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class LpLog:
    _instances = {}

    def __new__(cls, run_id: str = ""):
        if not run_id:
            run_id = Lo.current_doc.runtime_uid
        key = f"{cls.__name__}_{run_id}"
        if not key in cls._instances:
            inst = super(LpLog, cls).__new__(cls)
            inst._is_init = False
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, run_id: str = "") -> None:
        if getattr(self, "_is_init", False):
            return
        if not run_id:
            run_id = Lo.current_doc.runtime_uid
        log_name = self.__class__.__name__
        self._log_path = Lo.tmp_dir / f"{log_name}_{run_id}.log"
        log = LogInst()
        log.debug(f"LpLog - lp_log_path: {self._log_path}")
        self._log = OxtLogger(log_name=log_name, log_file=str(self._log_path), add_console_logger=True)
        self._log.setLevel(10)
        self._is_init = True

    @property
    def log(self) -> OxtLogger:
        return self._log

    @classmethod
    def reset_instance(cls, run_id: str) -> None:
        key = f"{cls.__name__}_{run_id}"
        if key in cls._instances:
            del cls._instances[key]

    @property
    def log_path(self) -> Path:
        return self._log_path


def lp_log(*args: Any, **kwargs: Any) -> None:
    log = LpLog(Lo.current_doc.runtime_uid).log
    log_mode = kwargs.pop("mode", "debug")
    if log_mode == "info":
        log.info(*args, **kwargs)
    elif log_mode in ("warn", "warning"):
        log.warning(*args, **kwargs)
    elif log_mode == "error":
        log.error(*args, **kwargs)
    else:
        log.debug(*args, **kwargs)
