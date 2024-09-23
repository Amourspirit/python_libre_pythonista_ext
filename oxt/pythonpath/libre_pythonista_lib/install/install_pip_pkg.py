from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
import re
import urllib.request
import urllib.error
import uno

from ooodev.loader import Lo
from ooodev.dialog.msgbox import MessageBoxResultsEnum, MessageBoxType, MsgBox

from ..dialog.install.remote_dlg_input import RemoteDlgInput


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.install.install_pkg import InstallPkg
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver

    from ....___lo_pip___.install.download import Download
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.install.install_pkg import InstallPkg

    from ___lo_pip___.install.download import Download
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class InstallPipPkg:

    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctx = Lo.get_context()
        self._rr = ResourceResolver(self._ctx)

    def install(self) -> None:
        """Install pip packages."""
        self._log.debug("InstallPipPkg.install()")
        dlg = RemoteDlgInput()
        result = dlg.show()
        if result == MessageBoxResultsEnum.OK.value:
            if not self._is_internet_connected():
                MsgBox.msgbox(
                    self._rr.resolve_string("msg07"),
                    title=self._rr.resolve_string("msg01"),
                    boxtype=MessageBoxType.ERRORBOX,
                )
                self._log.warning("Internet not connected.")
                return
            pkg = dlg.package_name
            name, ver = self._parse_pip_install_string(pkg)
            if not self._is_valid_pypi_package(name):
                msg = self._rr.resolve_string("msg12").format(name)  # Package {} not found
                MsgBox.msgbox(
                    msg,
                    title=self._rr.resolve_string("msg01"),
                    boxtype=MessageBoxType.ERRORBOX,
                )
                self._log.warning(f"Package {name} not found.")
                return
            self._install_pkg(name, ver, dlg.force_install)
        else:
            self._log.debug("User cancelled the install package operation.")
            return

    def _is_internet_connected(self) -> bool:
        """Check if the internet is connected."""
        return Download().is_internet

    def _parse_pip_install_string(self, pip_string: str) -> Tuple[str, str]:
        # Define the regex pattern to match the package name and version specifier
        pattern = r"^([a-zA-Z0-9\-_]+)(.*)$"

        # Search for the pattern in the input string
        match = re.match(pattern, pip_string)

        if match:
            # Extract the package name and the remaining string
            package_name = match.group(1)
            version_specifier = match.group(2).strip()
            result = package_name, version_specifier
            self._log.debug(f"Package name: {result[0]}, Version specifier: {result[1]}")
        else:
            result = pip_string, ""
            self._log.debug(f"Package name: {result[0]}, No version specifier")
        return result

    def _is_valid_pypi_package(self, package_name: str) -> bool:
        """Check if a package name is a valid PyPI package."""
        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            with urllib.request.urlopen(url) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise

    def _install_pkg(self, name: str, version: str, force: bool) -> None:
        """Install a package using pip."""
        self._log.debug(f"InstallPipPkg._install_pkg({name}, {version}, {force})")
        install = InstallPkg(ctx=self._ctx)
        result = install.install(req={name: version}, force=force)
        if result:
            MsgBox.msgbox(
                self._rr.resolve_string("msg13").format(name),  # Package {} installed successfully
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {name} installed successfully.")
        else:
            MsgBox.msgbox(
                self._rr.resolve_string("msg14").format(name),  # Package {} installation failed
                title=self._rr.resolve_string("msg01"),
                boxtype=MessageBoxType.ERRORBOX,
            )
            self._log.error(f"Package {name} installation failed.")
        self._log.debug("InstallPipPkg._install_pkg() completed.")
