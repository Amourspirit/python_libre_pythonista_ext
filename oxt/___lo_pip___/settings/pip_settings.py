from __future__ import annotations
from typing import cast, Tuple

from .settings import Settings
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration
from ..config import Config


class PipSettings(metaclass=Singleton):
    """Singleton Class. Manages Settings for the extension."""

    def __init__(self) -> None:
        settings = Settings()
        self._config = Config()
        self._configuration = Configuration()
        self._installed_local_pips = cast(Tuple, settings.current_settings.get("InstalledLocalPips", ()))
        self._node_value = f"/{settings.lo_implementation_name}.Settings/PipInfo"

    def append_installed_local_pip(self, pip_name: str) -> None:
        """Appends a pip to the installed local pips."""
        if pip_name not in self.installed_local_pips:
            self.installed_local_pips = (*self.installed_local_pips, pip_name)

    def remove_installed_local_pip(self, pip_name: str) -> None:
        """Removes a pip from the installed local pips."""
        if pip_name in self.installed_local_pips:
            self.installed_local_pips = tuple(pip for pip in self.installed_local_pips if pip != pip_name)

    @property
    def installed_local_pips(self) -> Tuple[str, ...]:
        """Gets/Sets the installed local pips."""
        return self._installed_local_pips

    @installed_local_pips.setter
    def installed_local_pips(self, value: Tuple[str, ...]) -> None:
        self._configuration.save_configuration_str_lst(
            node_value=self._node_value, name="InstalledLocalPips", value=value
        )
        self._installed_local_pips = value
