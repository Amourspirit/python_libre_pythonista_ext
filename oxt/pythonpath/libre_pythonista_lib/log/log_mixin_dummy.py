from __future__ import annotations

from .dummy_log import DummyLogger


class LogMixinDummy:
    def __init__(self) -> None:
        self._LogMixinDummy__log = DummyLogger(log_name=self.__class__.__name__)

    @property
    def log(self) -> DummyLogger:
        return self._LogMixinDummy__log

    @log.setter
    def log(self, value: DummyLogger) -> None:
        self._LogMixinDummy__log = value
