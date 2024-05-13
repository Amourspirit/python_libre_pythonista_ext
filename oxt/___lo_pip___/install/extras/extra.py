from __future__ import annotations
from typing import Any, Dict
from abc import ABC, abstractmethod

from ...config import Config


class Extra(ABC):
    """
    Installs Wheel package if it is not already installed.
    """

    def __init__(self, ctx: Any, **kwargs: Any) -> None:
        """
        Constructor

        Args:
            ctx (Any): The uno component context.

        Keyword Arguments:
            flag_upgrade {bool} -- Flag to upgrade package. Default True)
            show_progress {bool} -- Flag to show progress. Defaults to ``Config.show_progress``)
        """
        self.ctx = ctx
        self._config = Config()
        self._flag_upgrade = bool(kwargs.get("flag_upgrade", True))
        self._show_progress = bool(kwargs.get("show_progress", self._config.show_progress))

    def install(self) -> bool:
        """
        Install wheel if it is not already installed.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self._config.is_flatpak:
            return self._install_flatpak()

        return self._install_default()

    @abstractmethod
    def _get_packages(self) -> Dict[str, str]:
        """
        Gets the Package Names.
        """
        ...

    def _install_flatpak(self) -> bool:
        from ..pkg_installers.install_pkg_flatpak import InstallPkgFlatpak

        installer = InstallPkgFlatpak(ctx=self.ctx, flag_upgrade=self.flag_upgrade, show_progress=self.show_progress)
        return installer.install(self._get_packages())

    def _install_default(self) -> bool:
        from ..pkg_installers.install_pkg import InstallPkg

        installer = InstallPkg(ctx=self.ctx, flag_upgrade=self.flag_upgrade, show_progress=self.show_progress)
        return installer.install(self._get_packages())

    # region Properties
    @property
    def flag_upgrade(self) -> bool:
        """Gets/Sets the flag_upgrade."""
        return self._flag_upgrade

    @flag_upgrade.setter
    def flag_upgrade(self, value: bool) -> None:
        """Sets the flag_upgrade."""
        self._flag_upgrade = value

    @property
    def show_progress(self) -> bool:
        """Gets/Sets the show_progress."""
        return self._show_progress

    @show_progress.setter
    def show_progress(self, value: bool) -> None:
        """Sets the show_progress."""
        self._show_progress = value

    @property
    def config(self) -> Config:
        """Gets the config."""
        return self._config

    # endregion Properties
