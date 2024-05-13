from __future__ import annotations
from typing import Any, Dict, cast, TYPE_CHECKING
import uno

from ..lo_util.configuration import Configuration
from ..meta.singleton import Singleton
from ..oxt_logger import OxtLogger
from ..basic_config import BasicConfig

from ..events.lo_events import Events
from ..events.args import EventArgs
from ..events.named_events import ConfigurationNamedEvent, LogNamedEvent

if TYPE_CHECKING:
    from com.sun.star.configuration import ConfigurationAccess


class Settings(metaclass=Singleton):
    """Singleton Class. Manages Settings for the extension."""

    def __init__(self) -> None:
        self._logger: OxtLogger | None = None
        self._configuration = Configuration()
        cfg = BasicConfig()
        self._lo_identifier = cfg.lo_identifier
        self._lo_implementation_name = cfg.lo_implementation_name
        self._current_settings = self.get_settings()
        self._events = Events(source=self)
        self._set_events()

    def _set_events(self) -> None:
        def on_configuration_saved(src: Any, event_args: EventArgs) -> None:
            if self._logger:
                self._logger.debug("Settings. Configuration saved. Updating settings..")
            self._update_settings()

        def on_configuration_str_lst_saved(src: Any, event_args: EventArgs) -> None:
            if self._logger:
                self._logger.debug("Settings. Configuration str lst saved. Updating settings..")
            self._update_settings()

        def on_logging_ready(src: Any, event_args: EventArgs) -> None:
            # this class may be called before the logger is ready,
            # if so, we'll get a logger when the event is raised.
            # it is critical that trigger=False, otherwise we'll get an infinite loop.
            if self._logger is None:
                self._logger = OxtLogger(log_name=__name__, trigger=False)
                self._logger.debug("Created Logger.")

        # keep callbacks in scope
        self._fn_on_configuration_saved = on_configuration_saved
        self._fn_on_configuration_str_lst_saved = on_configuration_str_lst_saved
        self._fn_on_logging_ready = on_logging_ready

        self._events.on(event_name=ConfigurationNamedEvent.CONFIGURATION_SAVED, callback=on_configuration_saved)
        self._events.on(
            event_name=ConfigurationNamedEvent.CONFIGURATION_STR_LST_SAVED, callback=on_configuration_str_lst_saved
        )
        self._events.on(event_name=LogNamedEvent.LOGGING_READY, callback=on_logging_ready)

    def get_settings(self) -> Dict[str, Any]:
        # sourcery skip: dict-assign-update-to-union
        key = f"/{self.lo_implementation_name}.Settings"
        reader = cast("ConfigurationAccess", self._configuration.get_configuration_access(key))
        group_names = reader.getElementNames()
        settings = {}
        for groupname in group_names:
            group = cast("ConfigurationAccess", reader.getByName(groupname))
            props = group.getElementNames()
            values = group.getPropertyValues(props)
            # settings.update({k: v for k, v in zip(props, values)})
            settings.update(dict(zip(props, values)))
        if self._logger:
            self._logger.debug(f"Returning {self.lo_implementation_name} settings.")
        return settings

    def _update_settings(self) -> None:
        """Updates the current settings"""
        self._current_settings = self.get_settings()

    @property
    def lo_identifier(self) -> str:
        return self._lo_identifier

    @property
    def lo_implementation_name(self) -> str:
        return self._lo_implementation_name

    @property
    def current_settings(self) -> Dict[str, Any]:
        return self._current_settings

    @property
    def configuration(self) -> Configuration:
        return self._configuration
