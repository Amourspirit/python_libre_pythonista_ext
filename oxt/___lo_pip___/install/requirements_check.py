"""
Checks to see if Requirements are met for Pip packages.

No Internet needed.
"""

from __future__ import annotations

import importlib.util
from importlib.metadata import PackageNotFoundError, version

from ..config import Config
from ..ver.rules.ver_rules import VerRules
from ..oxt_logger import OxtLogger
from ..meta.singleton import Singleton
from .py_packages.packages import Packages
from .py_packages.py_package import PyPackage
from ..settings.install_settings import InstallSettings


class RequirementsCheck(metaclass=Singleton):
    """Requirements Check class."""

    def __init__(self) -> None:
        self._log = OxtLogger(log_name=__name__)
        self._config = Config()
        self._ver_rules = VerRules()

    def run_imports_ready(self, *other_mods: str) -> bool:
        """
        Check if the run imports are ready.

        Returns:
            bool: ``True`` if all run imports are ready; Otherwise, ``False``.
        """
        for oth in other_mods:
            spec = importlib.util.find_spec(oth)
            if spec is None:
                self._log.warning("Import %s failed.", oth)
                return False

        if not self._config.run_imports:
            return True

        for imp in self._config.run_imports:
            spec = importlib.util.find_spec(imp)
            if spec is None:
                self._log.warning("Import %s failed.", imp)
                return False

        if self._config.is_linux:
            for imp in self._config.run_imports_linux:
                spec = importlib.util.find_spec(imp)
                if spec is None:
                    self._log.warning("Import %s failed.", imp)
                    return False

        if self._config.is_mac:
            for imp in self._config.run_imports_macos:
                spec = importlib.util.find_spec(imp)
                if spec is None:
                    self._log.warning("Import %s failed.", imp)
                    return False

        if self._config.is_win:
            for imp in self._config.run_imports_win:
                spec = importlib.util.find_spec(imp)
                if spec is None:
                    self._log.warning("Import %s failed.", imp)
                    return False
        self._log.debug("All runtime imports are ready.")
        return True

    def check_requirements(self) -> bool:
        """
        Check requirements that have been set in file ``pyproject.toml`` in the ``tool.oxt.requirements`` section.

        Returns:
            bool: ``True`` if requirements are installed; Otherwise, ``False``.
        """
        install_settings = InstallSettings()
        config_req = self._config.requirements.copy()
        for pkg in install_settings.no_install_packages:
            if pkg in config_req:
                self._log.debug("Package %s is in the no install list. Not checking and continuing.", pkg)
                del config_req[pkg]

        requirements_met = all(self._is_valid_version(name=name, ver=ver) == 0 for name, ver in config_req.items())
        if not requirements_met:
            self._log.error("Requirements not met. Tested config requirements.")
            return False

        ver_rules = VerRules()

        def check_installed_valid(pkg: PyPackage) -> bool:
            nonlocal ver_rules, install_settings
            if pkg.name in install_settings.no_install_packages:
                self._log.debug("Package %s is in the no install list. Not checking and continuing.", pkg.name)
                return True
            ver_str = self._get_package_version(pkg.name)
            if not ver_str:
                self._log.debug("Package %s not installed ...", pkg.name)
                return False
            try:
                _, pkg_ver = pkg.name_version
                return ver_rules.get_installed_is_valid(vstr=pkg_ver, check_version=ver_str)
            except Exception as e:
                self._log.error(e)
            return False

        pkgs = Packages()
        requirements_met = all(check_installed_valid(pkg) for pkg in pkgs.packages)
        if not requirements_met:
            self._log.info("Requirements not met. Tested py_packages.")
            return False
        self._log.info("Requirements are met")
        return True

    def _get_package_version(self, package_name: str) -> str:
        """
        Get the version of an installed package.

        Args:
            package_name (str): The name of the package such as ``verr``

        Returns:
            str: The version of the package or an empty string if the package is not installed.
        """
        try:
            return version(package_name)
        except PackageNotFoundError:
            return ""

    def _is_valid_version(self, name: str, ver: str) -> int:
        """
        Check if the version of a package is valid.

        Args:
            name (str): The name of the package such as ``verr``. If empty string the version is converted to ``>=0.0.0``
            ver (str): The version of the package such as ``>=1.0.0``

        Returns:
            int: ``0`` if installed and requirements met, ``1`` if installed requirements not met, ``2`` if Not installed, ``-1`` if not valid
        """
        pkg_ver = self._get_package_version(name)
        if not pkg_ver:
            self._log.debug("Package %s not installed.", name)
            return 2

        if not ver:
            # set default version to >=0.0.0
            ver = "==*"
        rules = self._ver_rules.get_matched_rules(ver)
        self._log.debug("Found Package %s %s already installed ...", name, pkg_ver)
        if not rules:
            if pkg_ver:
                self._log.info("Package %s %s already installed, no rules", name, pkg_ver)
            else:
                self._log.error("Unable to find rules for %s %s", name, ver)
            return -1

        rules_pass = self._ver_rules.get_installed_is_valid_by_rules(rules=rules, check_version=pkg_ver)
        if rules_pass is False:
            self._log.info(
                "Package %s %s already installed. It does not meet requirements specified by: %s",
                name,
                pkg_ver,
                ver,
            )
            return 1
        self._log.info(
            "Package %s %s already installed. Requirements met for constraints: %s",
            name,
            pkg_ver,
            ver,
        )
        return 0
