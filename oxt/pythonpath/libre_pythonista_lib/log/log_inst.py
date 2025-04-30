from __future__ import annotations
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from oxt.___lo_pip___.oxt_logger import OxtLogger

_LOG_INST = None


def LogInst() -> OxtLogger:  # noqa: ANN202, N802
    global _LOG_INST
    if _LOG_INST:
        return _LOG_INST

    if "PYTEST_CURRENT_TEST" in os.environ:
        if TYPE_CHECKING:
            from oxt.pythonpath.libre_pythonista_lib.log.dummy_log import DummyLogger
        else:
            from libre_pythonista_lib.log.dummy_log import DummyLogger
        _LOG_INST = DummyLogger()
        return _LOG_INST  # type: ignore

    if not TYPE_CHECKING:
        from ___lo_pip___.oxt_logger import OxtLogger

    class _LogInst(OxtLogger):
        def __init__(self) -> None:
            log_name = "___lo_pip___"
            super().__init__(log_name=log_name)

    _LOG_INST = _LogInst()
    return _LOG_INST


# LogInst: OxtLogger = _get_logger()  # type: ignore
