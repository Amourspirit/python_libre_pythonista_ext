from __future__ import annotations
import os

import subprocess
from typing import Any, Dict, Union
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version

from ..config import Config
from ..ver.rules.ver_rules import VerRules
from ..oxt_logger import OxtLogger


# https://docs.python.org/3.8/library/importlib.metadata.html#module-importlib.metadata
# https://stackoverflow.com/questions/44210656/how-to-check-if-a-module-is-installed-in-python-and-if-not-install-it-within-t

# https://stackoverflow.com/search?q=%5Bpython%5D+run+subprocess+without+popup+terminal
# silent subprocess
if os.name == "nt":
    _si = subprocess.STARTUPINFO()
    _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    _si = None


class InstallPkg:
    """Install pip packages."""

    def __init__(self, ctx: Any, flag_upgrade: bool = True) -> None:  # noqa: ANN401
        self.ctx = ctx
        self._config = Config()
        self.path_python = Path(self._config.python_path)
        self.ver_rules = VerRules()
        self._logger = OxtLogger(log_name=__name__)
        self._flag_upgrade = flag_upgrade

    def install(self, req: Union[Dict[str, str], None] = None, force: bool = False) -> bool:
        """
        Install all the packages in the configuration if they are not already installed and meet requirements.

        Args:
            req (Dict[str, str], None, optional): The requirements to install.
                If omitted then requirements from config are used. Defaults to None.
            force (bool, optional): Force install even if package is already installed. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self._config.is_flatpak:
            self._logger.info("Flatpak detected, installing packages via Flatpak installer")
            result = self._install_flatpak(req=req, force=force)
            if not result:
                self._logger.error("Not all package were installed!")
            return result

        if self._config.is_win:
            self._logger.info("Windows detected, installing packages via Windows installer")
            result = self._install_win(req=req, force=force)
            if not result:
                self._logger.error("Not all package were installed!")
            return result

        self._logger.info("Installing packages via default installer")
        result = self._install_default(req=req, force=force)
        if not result:
            self._logger.error("Not all package were installed!")
        return result

    def install_file(self, pth: Union[str, Path], force: bool = False) -> bool:
        """
        Install a package from a file.

        Args:
            pth (str, Path): The path to the file to install.
            force (bool, optional): Force install even if package is already installed. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self._config.is_flatpak:
            self._logger.info("Flatpak detected, installing packages via Flatpak installer")
            result = self._install_flatpak_file(pth=pth, force=force)
            if not result:
                self._logger.error("install_file(): Not all package were installed!")
            return result

        if self._config.is_win:
            self._logger.info("Windows detected, installing packages via Windows installer")
            result = self._install_win_file(pth=pth, force=force)
            if not result:
                self._logger.error("install_file(): Not all package were installed!")
            return result
        self._logger.info("install_file(): Installing packages via default installer")
        result = self._install_default_file(pth=pth, force=force)
        if not result:
            self._logger.error("install_file(): Not all package were installed!")
        return result

    def uninstall(self, pkg: str, target: str = "", remove_tracking_file: bool = False) -> bool:
        """
        Uninstall a package.

        Args:
            pkg (str): The name of the package to uninstall.
            target (str, optional): The target to uninstall from. Defaults to "".
            remove_tracking_file (bool, optional): Remove the tracking file for the package. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self._config.is_flatpak:
            self._logger.info("Flatpak detected, uninstalling packages via Flatpak installer")
            result = self._uninstall_flatpak(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)
            if not result:
                self._logger.error("Not all package were uninstalled!")
            return result

        if self._config.is_win:
            self._logger.info("Windows detected, uninstalling packages via Windows installer")
            result = self._uninstall_win(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)
            if not result:
                self._logger.error("Not all package were uninstalled!")
            return result

        self._logger.info("Uninstalling packages via default installer")
        result = self._uninstall_default(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)
        if not result:
            self._logger.error("Not all package were uninstalled!")
        return result

    def _install_default(self, req: Union[Dict[str, str], None], force: bool) -> bool:
        from .pkg_installers.install_pkg import InstallPkg

        installer = InstallPkg(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install(req=req, force=force)

    def _install_win(self, req: Union[Dict[str, str], None], force: bool) -> bool:
        from .pkg_installers.install_pkg_win import InstallPkgWin

        installer = InstallPkgWin(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install(req=req, force=force)

    def _install_default_file(self, pth: Union[str, Path], force: bool = False) -> bool:
        from .pkg_installers.install_pkg import InstallPkg

        installer = InstallPkg(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install_file(pth=pth, force=force)

    def _install_win_file(self, pth: Union[str, Path], force: bool = False) -> bool:
        from .pkg_installers.install_pkg_win import InstallPkgWin

        installer = InstallPkgWin(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install_file(pth=pth, force=force)

    def _install_flatpak(self, req: Union[Dict[str, str], None], force: bool) -> bool:
        from .pkg_installers.install_pkg_flatpak import InstallPkgFlatpak

        installer = InstallPkgFlatpak(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install(req=req, force=force)

    def _install_flatpak_file(self, pth: Union[str, Path], force: bool = False) -> bool:
        from .pkg_installers.install_pkg_flatpak import InstallPkgFlatpak

        installer = InstallPkgFlatpak(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.install_file(pth=pth, force=force)

    def _uninstall_default(self, pkg: str, target: str = "", remove_tracking_file: bool = False) -> bool:
        from .pkg_installers.install_pkg import InstallPkg

        installer = InstallPkg(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.uninstall_pkg(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)

    def _uninstall_win(self, pkg: str, target: str = "", remove_tracking_file: bool = False) -> bool:
        from .pkg_installers.install_pkg_win import InstallPkgWin

        installer = InstallPkgWin(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.uninstall_pkg(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)

    def _uninstall_flatpak(self, pkg: str, target: str = "", remove_tracking_file: bool = False) -> bool:
        from .pkg_installers.install_pkg_flatpak import InstallPkgFlatpak

        installer = InstallPkgFlatpak(ctx=self.ctx, flag_upgrade=self._flag_upgrade)
        return installer.uninstall_pkg(pkg=pkg, target=target, remove_tracking_file=remove_tracking_file)

    def get_package_version(self, package_name: str) -> str:
        """
        Get the version of a package.

        Args:
            package_name (str): The name of the package such as ``verr``

        Returns:
            str: The version of the package or an empty string if the package is not installed.
        """
        try:
            return version(package_name)
        except PackageNotFoundError:
            return ""
