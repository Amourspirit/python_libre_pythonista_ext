from __future__ import annotations
import logging
import sys
import contextlib
from pathlib import Path
from typing import Any, Dict, Callable, TYPE_CHECKING
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from ooodev.loader import Lo
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const.event_const import LOG_PY_LOGGER_RESET, GBL_DOC_CLOSING
from ..event.shared_event import SharedEvent


from .event_log_handler import EventLogHandler
from ..doc_props.calc_props import CalcProps

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PyLogger(Logger):
    """
    Custom Logger Class.

    This class will only log to the Document that created the logger.
    """

    _instances: Dict[str, PyLogger] = {}

    def __new__(cls, doc: OfficeDocumentT):
        key = f"doc_{doc.runtime_uid}"
        if not key in cls._instances:
            inst = super(PyLogger, cls).__new__(cls)
            inst._is_init = False
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, doc: OfficeDocumentT):
        """
        Creates a logger.


        Args:
            doc (OfficeDocumentT): The document.

        Returns:
            None: None
        """
        if getattr(self, "_is_init", False):
            return
        self._uid = doc.runtime_uid
        self._otx_log = OxtLogger(log_name=self.__class__.__name__)
        self._otx_log.debug("Initializing PyLogger")
        calc_props = CalcProps(doc=doc)

        self._log_name = self.__class__.__name__
        self._formatter = logging.Formatter(calc_props.log_format)
        self._add_console_logger = calc_props.log_to_console
        self._log_level = calc_props.log_level
        self._log_file = Lo.tmp_dir / f"{self._log_name}_{self._uid}.log"
        self._log_extra_info = calc_props.include_extra_err_info

        logging.addLevelName(logging.ERROR, "ERROR")
        logging.addLevelName(logging.DEBUG, "DEBUG")
        logging.addLevelName(logging.INFO, "INFO")
        logging.addLevelName(logging.WARNING, "WARNING")
        logging.addLevelName(logging.CRITICAL, "CRITICAL")

        # Logger.__init__(self, name=log_name, level=cfg.log_level)
        super().__init__(name=self._log_name, level=self._log_level)

        has_handler = False
        has_console_handler = False

        self._event_log_handler = EventLogHandler(uid=self._uid)
        self._event_log_handler.setFormatter(self._formatter)
        self._otx_log.debug("Adding Event Log Handler")
        self.addHandler(self._event_log_handler)

        if self._log_file and self._log_level >= 10:  # DEBUG
            self._otx_log.debug("Adding File Handler")
            self.addHandler(self._get_file_handler())
            has_handler = True

        if self._add_console_logger and self._log_level > 0:
            self._otx_log.debug("Adding Console Handler")
            self.addHandler(self._get_console_handler())
            has_handler = True
            has_console_handler = True

        if not has_console_handler and self._add_console_logger:
            self._otx_log.debug("No Console Handler, adding one")
            self.addHandler(self._get_console_handler())
            has_handler = True
            has_console_handler = True

        if not has_handler:
            self.addHandler(self._get_null_handler())

        # with this pattern, it's rarely necessary to propagate the| error up to parent
        self.propagate = False
        if self._otx_log.is_debug:
            self._otx_log.debug(f"Logger {self._log_name} initialized with log level {self._log_level}")
            self._otx_log.debug(f"Logger is_debug: {self.is_debug}")
            self._otx_log.debug(f"Logger is_info: {self.is_info}")
            self._otx_log.debug(f"Logger is_warning: {self.is_warning}")
            self._otx_log.debug(f"Logger is_error: {self.is_error}")
            self._otx_log.debug(f"Logger log_file: {self.log_file}")
            self._otx_log.debug(f"Logger log_extra_info: {self.log_extra_info}")

            self._otx_log.debug("PyLogger Initialed")
        self._is_init = True

    def _get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._formatter)
        console_handler.setLevel(self._log_level)
        return console_handler

    def _get_null_handler(self):
        return logging.NullHandler()

    def _get_file_handler(self):
        log_file = self._log_file
        file_handler = TimedRotatingFileHandler(
            log_file, when="W0", interval=1, backupCount=3, encoding="utf8", delay=True
        )
        # file_handler = logging.FileHandler(log_file, mode="w", encoding="utf8", delay=True)
        file_handler.setFormatter(self._formatter)
        file_handler.setLevel(self._log_level)
        return file_handler

    def debugs(self, *messages: str) -> None:
        """
        Log Several messages debug formatted by tab.

        Args:
            messages (Any):  One or more messages to log.

        Return:
            None:
        """
        data = [str(m) for m in messages]
        self.debug("\t".join(data))
        return

    # region Events
    def subscribe_log_event(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_log_event(cb)
        self._event_log_handler.subscribe_event("log_emit", cb)

    def unsubscribe_log_event(self, cb: Callable[[Any, Any], None]) -> None:
        with contextlib.suppress(Exception):
            self._event_log_handler.unsubscribe_event("log_emit", cb)

    # endregion Events

    def _is_doc_match(self) -> bool:
        try:
            return self._uid == Lo.current_doc.runtime_uid
        except Exception as e:
            self._otx_log.error(f"_is_doc_match() Doc not available: {e}")
            return False

    # region Log Overrides:
    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=True)
        """
        if self.isEnabledFor(logging.DEBUG) and self._is_doc_match():
            super().debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=True)
        """
        if self.isEnabledFor(logging.INFO) and self._is_doc_match():
            super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=True)
        """
        if self.isEnabledFor(logging.WARNING) and self._is_doc_match():
            super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=True)
        """
        if self.isEnabledFor(logging.ERROR) and self._is_doc_match():
            super().error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=True)
        """
        if self.isEnabledFor(logging.CRITICAL) and self._is_doc_match():
            super().critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=True)
        """
        if self._is_doc_match():
            super().log(level, msg, *args, **kwargs)

    # endregion Log Overrides

    # region Properties
    @property
    def is_debug(self) -> bool:
        """Check if is debug"""
        return self.isEnabledFor(logging.DEBUG)

    @property
    def is_info(self) -> bool:
        """Check if is info"""
        return self.isEnabledFor(logging.INFO)

    @property
    def is_warning(self) -> bool:
        """Check if is warning"""
        return self.isEnabledFor(logging.WARNING)

    @property
    def is_error(self) -> bool:
        """Check if is error"""
        return self.isEnabledFor(logging.ERROR)

    @property
    def log_file(self) -> Path:
        """Check if is critical"""
        return self._log_file

    @property
    def log_extra_info(self) -> bool:
        """Gets if Extra Log info should be include in Errors"""
        return self._log_extra_info

    # endregion Properties

    @classmethod
    def reset_instance(cls, doc: OfficeDocumentT | None = None) -> None:
        """
        Reset the Singleton instance(s).

        Args:
            doc (CalcDoc | None, optional): Calc Doc or None. If None all cached instances are cleared. Defaults to None.
        """
        se = SharedEvent(doc=doc)
        if doc is None:
            cls._instances = {}
            eargs = EventArgs(cls)
            eargs.event_data = DotDict(reset_all=True, runtime_id="")
            se.trigger_event(LOG_PY_LOGGER_RESET, eargs)
            return
        key = f"doc_{doc.runtime_uid}"
        if key in cls._instances:
            del cls._instances[key]
            eargs = EventArgs(cls)
            eargs.event_data = DotDict(reset_all=False, runtime_id=doc.runtime_uid)
            se.trigger_event(LOG_PY_LOGGER_RESET, eargs)


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"doc_{uid}"
    if key in PyLogger._instances:
        del PyLogger._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
