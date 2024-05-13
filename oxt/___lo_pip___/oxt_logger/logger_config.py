from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING
from pathlib import Path

from ..basic_config import BasicConfig
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration
from ..input_output import file_util
from ..events.lo_events import LoEvents
from ..events.args import EventArgs
from ..events.named_events.log_named_event import LogNamedEvent


if TYPE_CHECKING:
    from com.sun.star.configuration import ConfigurationAccess


class LoggerConfig(metaclass=Singleton):
    def __init__(self) -> None:
        basic_config = BasicConfig()
        self._lo_implementation_name = basic_config.lo_implementation_name
        # self._lo_implementation_name = settings.current_settings["lo_implementation_name"]
        configuration_settings = self._get_settings()
        log_file = str(configuration_settings["LogFile"])
        self._log_file = str(Path(file_util.get_user_profile_path(True), log_file))

        self._log_format = str(configuration_settings["LogFormat"])
        self._log_name = str(configuration_settings["LogName"])

        log_level = str(configuration_settings["LogLevel"])
        self._log_level = self._get_log_level(log_level)
        self._log_ready_event_raised = False
        self._log_add_console = bool(configuration_settings["LogAddConsole"])

    def _get_settings(self) -> Dict[str, Any]:
        # sourcery skip: dict-assign-update-to-union
        configuration = Configuration()
        key = f"/{self.lo_implementation_name}.Settings"
        reader = cast("ConfigurationAccess", configuration.get_configuration_access(key))
        # group_names = reader.getElementNames()
        settings = {}

        log_group = cast("ConfigurationAccess", reader.getByName("Logging"))
        log_props = log_group.getElementNames()
        log_values = log_group.getPropertyValues(log_props)
        # settings.update({k: v for k, v in zip(log_props, log_values)})
        settings.update(dict(zip(log_props, log_values)))
        return settings

    def _get_log_level(self, log_level: str) -> int:
        log_level = log_level.upper()
        if log_level == "NONE":
            return 0
        if log_level == "DEBUG":
            return 10
        elif log_level == "INFO":
            return 20
        elif log_level == "WARNING":
            return 30
        elif log_level == "ERROR":
            return 40
        elif log_level == "CRITICAL":
            return 50
        else:
            raise ValueError(f"Invalid log level: {log_level}")

    def trigger_log_ready_event(self) -> None:
        """
        Raises the log ready event. ``LogNamedEvent.LOGGING_READY`` named event.

        When a logger is created, it will raise this event to signal that the logger is ready.
        The event args ``event_data`` will contain a dictionary with the key ``first_time`` and a boolean value indicating if this the first time the event has been raised.
        """
        event_args = EventArgs("LoggerConfig.raise_log_ready_event")
        event_args.event_data = {"first_time": not self._log_ready_event_raised}
        LoEvents().trigger(event_name=LogNamedEvent.LOGGING_READY, event_args=event_args)
        self._log_ready_event_raised = True

    @property
    def lo_implementation_name(self) -> str:
        return self._lo_implementation_name

    @property
    def log_add_console(self) -> bool:
        """Gets if a console logger should be added to logging."""
        return self._log_add_console

    @property
    def log_file(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_file)
        """
        return self._log_file

    @property
    def log_format(self) -> str:
        """
        Gets the log format.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_format)
        """
        return self._log_format

    @property
    def log_name(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_name)
        """
        return self._log_name

    @property
    def log_level(self) -> int:
        """
        Gets the log level.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_level)
        """
        return self._log_level
