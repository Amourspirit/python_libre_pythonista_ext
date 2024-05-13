"""Install any local packages that are not already installed."""
from __future__ import annotations
from pathlib import Path
from typing import Any, List

from .install_pkg import InstallPkg
from ..config import Config
from ..oxt_logger import OxtLogger
from ..settings.pip_settings import PipSettings


class InstallPkgLocal:
    """Install local pip packages."""

    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx
        self._config = Config()
        self._logger = OxtLogger(log_name=__name__)

    def _get_local_packages(self) -> List[Path]:
        """Get a list of local packages to install."""

        local_pth = self._config.package_location / "local"
        if not local_pth.exists():
            return []
        result: List[Path] = []
        for pkg in local_pth.iterdir():
            if pkg.is_file():
                lower_name = pkg.name.lower()
                if lower_name.endswith(".whl") or lower_name.endswith(".tar.gz"):
                    result.append(pkg)
        return result

    def install(self) -> bool:
        """
        Install any local packages that are not already installed.

        Returns:
            bool: True if successful installing all local packages, False otherwise.
        """
        # sourcery skip: use-named-expression
        self._logger.debug("Install any local packages that are not already installed.")
        local_pkgs = self._get_local_packages()
        if not local_pkgs:
            self._logger.debug("No local packages to install.")
            return False

        self._logger.debug(f"Found {len(local_pkgs)} Local packages to install")
        installer = InstallPkg(ctx=self.ctx, flag_upgrade=False)
        pi = PipSettings()

        installed_count = 0
        success = True
        for pkg in local_pkgs:
            if pkg.name in pi.installed_local_pips:
                self._logger.info(f"Local package {pkg.name} is already installed.")
                continue
            result = installer.install_file(pth=pkg, force=False)
            if result:
                pi.append_installed_local_pip(pkg.name)
                installed_count += 1
            else:
                self._logger.error(f"Failed to install local package: {pkg.name}")
            success = success and result
        if installed_count > 0:
            # Update the installed local pips to reflect the files that have been installed
            self._logger.debug(f"Updating installed local pips. Added {installed_count} new packages.")
            # pi.installed_local_pips = (*pi.installed_local_pips, *new_pkgs)
        else:
            self._logger.debug("No new local packages installed.")
        if success:
            self._logger.info("Finished installing local packages.")
        else:
            self._logger.error("Failed to install all local packages.")
        return success
