from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger import OxtLogger
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
else:
    from ___lo_pip___.oxt_logger import OxtLogger
    from libre_pythonista_lib.doc.doc_globals import DocGlobals


class LogMixin:
    def __init__(self) -> None:
        self.__log = self._get_logger_instance()

    def _get_logger_instance(self) -> OxtLogger:
        # gbl_cache = DocGlobals.get_current()
        if DocGlobals.is_pytest_running:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.log.dummy_log import DummyLogger
            else:
                from libre_pythonista_lib.log.dummy_log import DummyLogger
            return DummyLogger()  # type: ignore
        else:
            return OxtLogger(log_name=self.__class__.__name__)

    @property
    def log(self) -> OxtLogger:
        return self.__log

    @log.setter
    def log(self, value: OxtLogger) -> None:
        self.__log = value
