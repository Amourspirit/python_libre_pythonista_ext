from __future__ import annotations
from typing import cast, Tuple, Set

from .settings import Settings
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration


class InstallSettings(metaclass=Singleton):
    """
    Singleton Class. Manages Install Setting for the extension.
    """

    def __init__(self) -> None:
        settings = Settings()
        self._configuration = Configuration()
        self._node_value = f"/{settings.lo_implementation_name}.Settings/Install"
        self._no_install_packages = cast(
            Set[str], set(cast(Tuple, settings.current_settings.get("NoInstallPackages", ())))
        )

    # region Properties

    @property
    def no_install_packages(self) -> Set[str]:
        """
        Gets/Sets Pip Packages that are to be ignored.

        Generally adding and removing from this list would be done in extension settings.
        """
        return self._no_install_packages

    @no_install_packages.setter
    def no_install_packages(self, value: Set[str]) -> None:
        self._configuration.save_configuration_str_lst(
            node_value=self._node_value, name="NoInstallPackages", value=tuple(value)
        )
        self._no_install_packages = value

    # endregion Properties
