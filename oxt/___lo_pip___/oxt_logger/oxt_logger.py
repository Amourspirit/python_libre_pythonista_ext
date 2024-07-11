import logging
import sys
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

# from .. import config
from .logger_config import LoggerConfig


# https://stackoverflow.com/questions/13521981/implementing-an-optional-logger-in-code

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

        Returns:
            None: None
        """
        self._config = LoggerConfig()  # config.Config()
        self.formatter = logging.Formatter(self._config.log_format)
        if not log_file:
            log_file = self._config.log_file
        self._log_file = log_file
        if not log_name:
            log_name = self._config.log_name
        self.log_name = log_name

        # Logger.__init__(self, name=log_name, level=cfg.log_level)
        super().__init__(name=log_name, level=self._config.log_level)

        has_handler = False

        if self._log_file and self._config.log_level >= 10:  # DEBUG
            self.addHandler(self._get_file_handler())
            has_handler = True

        if self._config.log_add_console and self._config.log_level > 0:
            self.addHandler(self._get_console_handler())
            has_handler = True

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

    @property
    def log_file(self):
        """Log file path."""
        return self._log_file
