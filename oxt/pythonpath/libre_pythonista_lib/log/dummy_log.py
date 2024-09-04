import logging
import sys
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

# from .. import config


# https://stackoverflow.com/questions/13521981/implementing-an-optional-logger-in-code


class DummyLogger:
    """Dummy Logger Class. Does Nothing!"""

    def __init__(self, log_file: str = "", log_name: str = "", *args, **kwargs):

        pass

    def debugs(self, *messages: str) -> None:

        pass

    # region Logger Methods

    def setLevel(self, level):
        pass

    def debug(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def warn(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def exception(self, msg, *args, exc_info=True, **kwargs):
        pass

    def critical(self, msg, *args, **kwargs):
        pass

    def fatal(self, msg, *args, **kwargs):
        pass

    def log(self, level, msg, *args, **kwargs):
        pass

    def findCaller(self, stack_info=False, stacklevel=1):
        pass

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        pass

    def handle(self, record):
        pass

    def addHandler(self, hdlr):
        pass

    def removeHandler(self, hdlr):
        pass

    def hasHandlers(self):

        return False

    def callHandlers(self, record):

        pass

    def getEffectiveLevel(self):

        return 0

    def isEnabledFor(self, level):

        return False

    def getChild(self, suffix):

        return None

    def __repr__(self):

        return f"<{self.__class__.__name__}()>"

    def __reduce__(self):
        return None

    # endregion Logger Methods

    # region Properties

    @property
    def log_file(self):
        """Log file path."""
        ""

    @property
    def is_debug(self) -> bool:
        """Check if is debug"""
        return False

    @property
    def is_info(self) -> bool:
        """Check if is info"""
        return False

    @property
    def is_warning(self) -> bool:
        """Check if is warning"""
        return False

    @property
    def is_error(self) -> bool:
        """Check if is error"""
        return False

    # endregion Properties
