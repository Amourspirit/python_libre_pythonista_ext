from __future__ import annotations
from typing import TYPE_CHECKING
import importlib.util
import uno

from ooodev.loader import Lo
from ooodev.dialog.msgbox import MessageBoxType, MsgBox
from ooodev.dialog.input import Input


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver


class PkgInfo:

    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._ctx = Lo.get_context()
        self._rr = ResourceResolver(self._ctx)
        self._config = Config()

    def show_installed(self) -> None:
        """Install pip packages."""
        self._log.debug("InstallPipPkg.show_installed()")
        pkg_name = Input.get_input(
            title="Package Check",
            msg="Enter the package name",
            ok_lbl=self._rr.resolve_string("dlg01"),
            cancel_lbl=self._rr.resolve_string("dlg02"),
        )
        self._log.debug(f"show_installed() Package name: {pkg_name}")
        pkg_name = pkg_name.strip()
        if not pkg_name:
            self._log.debug("show_installed() No input.")
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg008"),
                title=self._rr.resolve_string("mbtitle008"),
                boxtype=MessageBoxType.INFOBOX,
            )
            return

        if self.is_package_installed(pkg_name):
            ver = self.get_package_version(pkg_name)
            if ver:
                msg = self._rr.resolve_string("mbmsg011").format(pkg_name, ver)  # Package {} version {} is installed
            else:
                msg = self._rr.resolve_string("mbmsg009").format(pkg_name)  # Package {} is installed
            MsgBox.msgbox(
                msg,  # Package {} is installed
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {pkg_name} is installed.")
        else:
            MsgBox.msgbox(
                self._rr.resolve_string("mbmsg010").format(pkg_name),  # Package {} is not installed
                title=self._rr.resolve_string("title02"),
                boxtype=MessageBoxType.INFOBOX,
            )
            self._log.info(f"Package {pkg_name} is not installed.")

    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed."""
        package_spec = importlib.util.find_spec(package_name)
        if self._log.is_debug and package_spec:
            self._log.debug(f"Package {package_name} spec. {package_spec}")
        return package_spec is not None

    def get_package_version(self, package_name: str) -> str:
        try:
            import pkg_resources
        except ImportError:
            self._log.exception("get_package_version() Package not found: pkg_resources")
            return ""
        try:
            version = pkg_resources.get_distribution(package_name).version
            return version
        except pkg_resources.DistributionNotFound:
            self._log.debug(f"get_package_version() Package {package_name} not found")
            return ""
