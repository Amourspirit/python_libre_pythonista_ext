from __future__ import annotations

from .settings import Settings
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration
from ..basic_config import BasicConfig


class InstallSettings(metaclass=Singleton):
    """Singleton Class. Manages Settings for the extension."""

    def __init__(self) -> None:
        settings = Settings()
        self._configuration = Configuration()
        self._node_value = f"/{settings.lo_implementation_name}.Settings/Install"
        self._install_ooodev = bool(settings.current_settings.get("InstallOooDev", True))
        self._install_odfpy = bool(settings.current_settings.get("InstallOdfpy", True))

    def update_config(self) -> None:
        """Updates the configuration by removing any requirements that are marked as do not install."""
        cfg = BasicConfig()
        if not self.install_ooodev:
            if "ooo-dev-tools" in cfg.requirements:
                _ = cfg.requirements.pop("ooo-dev-tools")
        if not self.install_odfpy:
            if "odfpy" in cfg.requirements:
                _ = cfg.requirements.pop("odfpy")

    # region Properties
    @property
    def install_ooodev(self) -> bool:
        """
        Gets the flag indicating if the startup should be delayed.
        """
        return self._install_ooodev

    @property
    def install_odfpy(self) -> bool:
        """
        Gets the flag indicating if the startup should be delayed.
        """
        return self._install_odfpy

    # endregion Properties
