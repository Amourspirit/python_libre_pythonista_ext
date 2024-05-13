from __future__ import annotations
import os
import platform
from pathlib import Path
import site
from ..config import Config
from ..meta.singleton import Singleton


class TargetPath(metaclass=Singleton):
    """Manages the target path for packages."""

    def __init__(self) -> None:
        self._config = Config()
        self._target = self._get_target()

    def _get_target(self) -> str:
        if not self._config.is_win:
            return self.config.site_packages
        if self.config.is_shared_installed or self.config.is_bundled_installed:
            return self.config.site_packages
        if self.has_other_target:
            return self._get_windows_target()
        return self.config.site_packages

    def _get_windows_target(self) -> str:
        # get path such as C:\Users\user\AppData\Roaming\Python
        is_32_bit = platform.architecture()[0] == "32bit"
        install_dir = Path(site.USER_BASE) if site.USER_BASE else Path(str(os.getenv("APPDATA"))) / "Roaming/Python"
        bits = "32" if is_32_bit else "64"
        target = install_dir / f"Python{self._config.python_major_minor.replace('.', '')}/{bits}/site-packages"
        return str(target)

    def ensure_exist(self) -> None:
        """Ensures the target path exists."""
        target = Path(self._target)
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)

    def exist(self) -> bool:
        """Gets if the target path exists."""
        return Path(self._target).exists()

    def get_package_target(self, pkg_name: str) -> str:
        """
        Gets a target path for the package.

        If not windows then the ``site-packages`` path is returned from config.

        If there is no isolated packages, then the site-packages path is returned.
        If the package is in the isolated list, then path such as ``C:\\Users\\user\\AppData\\Roaming\\Python`` is returned.

        Args:
            pkg_name (str): package name such as ``numpy``

        Returns:
            str: Package target path.
        """
        if self.has_other_target is False:
            return self._config.site_packages
        if pkg_name in self._config.isolate_windows:
            return self._target
        return self._config.site_packages

    @property
    def has_other_target(self) -> bool:
        """Gets if the extension has any isolated packages. Always returns ``False`` if not windows."""
        return len(self._config.isolate_windows) > 0 if self._config.is_win else False

    @property
    def target(self) -> str:
        """
        Gets the target path.

        This will be the ``site-packages`` path if not Windows or there are no isolated packages.
        """
        return self._target

    @property
    def config(self) -> Config:
        """Gets the config."""
        return self._config
