import logging
import sys
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from contextlib import contextmanager

# from .. import config
from .logger_config import LoggerConfig
from ..basic_config import BasicConfig


# https://stackoverflow.com/questions/13521981/implementing-an-optional-logger-in-code

_INDENT = 0


class OxtLogger(Logger):
    """Custom Logger Class"""

    def __init__(self, log_file: str = "", log_name: str = "", *args, **kwargs):
        """
        Creates a logger.

        Each time a logger is created it will raise the ``LogNamedEvent.LOGGING_READY`` event,
        unless the ``trigger`` keyword argument is set to ``False``.
        If you are creating a logger from the ``LogNamedEvent.LOGGING_READY`` event handler, then set ``trigger`` to ``False``;
        Otherwise, you will get an infinite loop.

        See ``settings.Settings._set_events()`` for an example of the ``LogNamedEvent.LOGGING_READY`` event.

        Args:
            log_file (str, optional): Log file. Defaults to configuration value.
            log_name (str, optional): Log Name. Defaults to configuration value.
            trigger (bool, optional): Trigger log ready event. Defaults to True.
            add_console_logger (bool, optional): Add console logger. Defaults to False.
                If The config setting have console logger enabled, it will be added automatically.

        Returns:
            None: None
        """
        global _INDENT
        self._config = LoggerConfig()  # config.Config()
        basic_config = BasicConfig()
        self._indent_amt = basic_config.log_indent
        if self._indent_amt > 0:
            self._fn_on_callback = self._on_callback
            # "%(asctime)s %(levelname)s: %(indent_str)s%(message)s"
            self.formatter = CallbackFormatter(fmt=self._config.log_format, callback=self._fn_on_callback)
        else:
            self.formatter = logging.Formatter(self._config.log_format)
        add_console_logger = kwargs.get("add_console_logger", False)

        if not log_file:
            log_file = self._config.log_file
        self._log_file = log_file
        if not log_name:
            log_name = self._config.log_name
        self.log_name = log_name

        logging.addLevelName(logging.ERROR, "ERROR")
        logging.addLevelName(logging.DEBUG, "DEBUG")
        logging.addLevelName(logging.INFO, "INFO")
        logging.addLevelName(logging.WARNING, "WARNING")

        # Logger.__init__(self, name=log_name, level=cfg.log_level)
        super().__init__(name=log_name, level=self._config.log_level)

        has_handler = False
        has_console_handler = False

        if self._log_file and self._config.log_level >= 10:  # DEBUG
            self.addHandler(self._get_file_handler())
            has_handler = True

        if self._config.log_add_console and self._config.log_level > 0:
            self.addHandler(self._get_console_handler())
            has_handler = True
            has_console_handler = True

        if not has_console_handler and add_console_logger:
            self.addHandler(self._get_console_handler())
            has_handler = True
            has_console_handler = True

        if not has_handler:
            self.addHandler(self._get_null_handler())

        # with this pattern, it's rarely necessary to propagate the| error up to parent
        self.propagate = False
        # signal that the logger is ready
        trigger = bool(kwargs.get("trigger", True))
        if trigger:
            self._config.trigger_log_ready_event()

    def _get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        console_handler.setLevel(self._config.log_level)
        return console_handler

    def _get_null_handler(self):
        return logging.NullHandler()

    def _get_file_handler(self):
        log_file = self._log_file
        file_handler = TimedRotatingFileHandler(
            log_file, when="W0", interval=1, backupCount=3, encoding="utf8", delay=True
        )
        # file_handler = logging.FileHandler(log_file, mode="w", encoding="utf8", delay=True)
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(self._config.log_level)
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

    def _on_callback(self, record):
        if self.current_indent > 0:
            s = " " * self.current_indent
        else:
            s = ""
        record.indent_str = s

    # region Indent
    def _core_indent(self, amount: int):
        """Core functionality for indentation."""
        self.current_indent = max(0, self.current_indent + amount)

    @contextmanager
    def indent(self, use_as_context_manager: bool = False):
        if use_as_context_manager:
            # Context manager behavior
            try:
                self._core_indent(self._indent_amt)
                yield self.current_indent
            finally:
                self._core_indent(-self._indent_amt)
        else:
            # Normal method behavior
            self._core_indent(self._indent_amt)
            return self.current_indent  # Optionally return something

    def outdent(self) -> int:
        self.current_indent = max(0, self.current_indent - self._indent_amt)
        return self.current_indent

    @contextmanager
    def noindent(self):
        """Temporarily disable indentation."""
        try:
            indent = self.current_indent
            self.current_indent = 0
            yield
        finally:
            self.current_indent = indent

    # endregion Indent

    # region Properties
    @property
    def log_file(self):
        """Log file path."""
        return self._log_file

    @property
    def is_debug(self) -> bool:
        """Check if is debug"""
        return self._config.log_level <= logging.DEBUG

    @property
    def is_info(self) -> bool:
        """Check if is info"""
        return self._config.log_level <= logging.INFO

    @property
    def is_warning(self) -> bool:
        """Check if is warning"""
        return self._config.log_level <= logging.WARNING

    @property
    def is_error(self) -> bool:
        """Check if is error"""
        return self._config.log_level <= logging.ERROR

    @property
    def current_indent(self) -> int:
        """
        Gets/Set the indent level.

        This is a global value that is shared across all instances of the logger.
        """
        global _INDENT
        return _INDENT

    @current_indent.setter
    def current_indent(self, value: int):
        global _INDENT
        _INDENT = value

    # endregion Properties


class CallbackFormatter(logging.Formatter):
    # https://stackoverflow.com/questions/17558552/how-do-i-add-custom-field-to-python-log-format-string
    def __init__(self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None, callback=None):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate, defaults=defaults)  # type: ignore
        self.callback = callback

    def format(self, record):
        # Execute the callback with the log record if a callback is provided
        if self.callback:
            self.callback(record)
        # Proceed with the normal formatting process
        return super().format(record)

    # def formatMessage(self, record):
    #     return super().formatMessage(record)
