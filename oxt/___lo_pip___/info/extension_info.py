from __future__ import annotations
from typing import cast, Any, Tuple, TYPE_CHECKING
from logging import Logger
import uno

from com.sun.star.deployment import XPackageInformationProvider
from com.sun.star.deployment import XPackage

from ..meta.singleton import Singleton

# from ..lo_util import Util

if TYPE_CHECKING:
    from com.sun.star.deployment import ExtensionManager  # service


class ExtensionInfo(metaclass=Singleton):
    """
    Gets info for an installed extension in LibreOffice.

    Singleton Class.
    """

    def get_extension_info(self, id: str) -> Tuple[str, ...]:
        """
        Gets info for an installed extension in LibreOffice.

        Args:
            id (str): Extension id

        Returns:
            Tuple[str, ...]: Extension info
        """
        # sourcery skip: use-next
        try:
            pip = self.get_pip()
        except Exception:
            return ()
        exts_tbl = pip.getExtensionList()
        for el in exts_tbl:
            if el[0] == id:
                return el
        return ()

    def get_pip(self) -> XPackageInformationProvider:
        """
        Gets Package Information Provider

        Raises:
            Exception: if unable to obtain XPackageInformationProvider interface

        Returns:
            XPackageInformationProvider: Package Information Provider
        """
        # sourcery skip: raise-specific-error
        ctx: Any = uno.getComponentContext()
        pip = ctx.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
        if pip is None:
            raise Exception("Unable to get PackageInformationProvider, pip is None")
        return cast(XPackageInformationProvider, pip)

    def get_extension_manager(self) -> ExtensionManager:
        ctx: Any = uno.getComponentContext()
        return ctx.getValueByName("/singletons/com.sun.star.deployment.ExtensionManager")

    def get_extension_details(self, pkg_id: str) -> Tuple[XPackage, ...]:
        """
        Gets details for an installed extension in LibreOffice

        Gets a tuple of three objects. Each object can be a XPackage or None.

        - First object represents the extension that is installed in the user layer.
        - Second object represents the extension that is installed in the shared layer.
        - Third object represents the extension that is installed in the bundled layer.

        Args:
            pkg_id (str):  Package ID. This is usually the ``lo_identifier`` value from pyproject.toml (tool.oxt.config),
                also found in the runtime Config class

        Returns:
            Tuple[XPackage, ...]: Return a tuple of three objects
        """
        # The last arg of getExtensionsWithSameIdentifier() should be XCommandEnvironment implementation.
        # It seems SmoketestCommandEnvironment fits the bill.
        # However, it will cause an error if Java (JRE) is not available. Simply put LibreOffice will show a popup dialog asking if you want to enable Java.
        # On an older Mac, It say that Java is corrupted and a new version needs to be installed.
        # Setting smoke to None seems to work fine.
        # This next line can break the extension due to Java requirement.
        # smoke = Util().create_uno_service("com.sun.star.deployment.test.SmoketestCommandEnvironment")
        smoke = None
        pip = self.get_pip()
        filename = pip.getPackageLocation(pkg_id)
        mgr = self.get_extension_manager()
        return mgr.getExtensionsWithSameIdentifier(pkg_id, filename, smoke)  # type: ignore

    def get_extension_loc(self, pkg_id: str, as_sys_path: bool = True) -> str:
        """
        Gets location for an installed extension in LibreOffice

        Args:
            pkg_id (str): This is usually the ``lo_identifier`` value from pyproject.toml (tool.oxt.config),
                also found in the runtime Config class
            as_sys_path (bool, optional): If True, returns the path as a system path entry otherwise ``file:///`` format.
                Defaults to True.

        Returns:
            str: Extension location on success; Otherwise, an empty string
        """
        try:
            pip = self.get_pip()
        except Exception:
            return ""
        if result := pip.getPackageLocation(pkg_id):
            return uno.fileUrlToSystemPath(result) if as_sys_path else result
        else:
            return ""

    def get_all_extensions(self) -> Tuple[Tuple[str, ...], ...]:
        """
        Gets info for all installed extensions in LibreOffice

        Returns:
            Tuple[Tuple[str, ...], ...]: Extension info
        """
        try:
            pip = self.get_pip()
        except Exception:
            return ()
        return pip.getExtensionList()

    def log_extensions(self, logger: Logger) -> None:
        """
        Logs extensions to log file

        Args:
            logger (Logger): Logger instance
        """
        try:
            pip = self.get_pip()
        except Exception:
            logger.debug("No package info provider found")
            return
        exts_tbl = pip.getExtensionList()
        logger.debug("Extensions:")
        for i in range(len(exts_tbl)):
            logger.debug(f"{i+1}. ID: {exts_tbl[i][0]}")
            logger.debug(f"   Version: {exts_tbl[i][1]}")
            logger.debug(f"   Loc: {pip.getPackageLocation(exts_tbl[i][0])}")
