from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from pathlib import Path
from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ...log.py_logger import PyLogger
from ...const.event_const import LOG_OPTIONS_CHANGED, LOG_PY_LOGGER_RESET
from ...event.shared_event import SharedEvent

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT


class LpLog:
    _instances = {}

    def __new__(cls):
        doc = Lo.current_doc
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            inst = super(LpLog, cls).__new__(cls)
            inst._is_init = False
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        self._fn_on_log_options_changed = self._on_log_options_changed
        self._share_event = SharedEvent()  # singleton
        self._share_event.subscribe_event(LOG_OPTIONS_CHANGED, self._fn_on_log_options_changed)
        _ = self.log
        self._is_init = True

    def _on_log_options_changed(self, src: Any, event_args: EventArgs) -> None:
        self._share_event.unsubscribe_event(LOG_OPTIONS_CHANGED, self._fn_on_log_options_changed)
        LpLog.reset_instance()

    @property
    def log(self) -> PyLogger:
        return PyLogger(Lo.current_doc)

    @classmethod
    def reset_instance(cls) -> None:
        doc = Lo.current_doc
        PyLogger.reset_instance(doc)
        key = f"doc_{doc.runtime_uid}"
        if key in cls._instances:
            inst = cls._instances[key]
            inst._share_event.unsubscribe_event(LOG_OPTIONS_CHANGED, inst._fn_on_log_options_changed)
            del cls._instances[key]

    @property
    def log_path(self) -> Path:
        return self.log.log_file

    @property
    def log_extra_info(self) -> bool:
        """Gets if Extra Log info should be include in Errors"""
        return self.log.log_extra_info


class StaticLpLog:

    @staticmethod
    def _get_logger() -> PyLogger:
        return LpLog().log

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.error(msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.exception(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        log = cls._get_logger()
        log.critical(msg, *args, **kwargs)
