from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from pathlib import Path

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.log.py_logger import PyLogger
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import LOG_OPTIONS_CHANGED
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.utils.singleton_base import SingletonBase
else:
    from libre_pythonista_lib.log.py_logger import PyLogger
    from libre_pythonista_lib.const.event_const import LOG_OPTIONS_CHANGED
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.utils.singleton_base import SingletonBase

    OfficeDocumentT = Any


class LpLog(SingletonBase):
    # _instances = {}

    # def __new__(cls):
    #     doc = Lo.current_doc
    #     key = f"doc_{doc.runtime_uid}"
    #     if not key in cls._instances:
    #         inst = super(LpLog, cls).__new__(cls)
    #         inst._is_init = False
    #         cls._instances[key] = inst
    #     return cls._instances[key]

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
        LpLog.remove_this_instance(self)

    @property
    def log(self) -> PyLogger:
        """Gets the logger"""
        doc = cast(OfficeDocumentT, Lo.current_doc)
        if doc is None:
            raise RuntimeError("Current document is None")
        return PyLogger(doc)

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
