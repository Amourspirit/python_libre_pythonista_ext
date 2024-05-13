"""
Checks to see if Requirements are met for Pip packages.

No Internet needed.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ..config import Config
from ..ver.rules.ver_rules import VerRules
from ..oxt_logger import OxtLogger
from ..meta.singleton import Singleton


class RequirementsCheck(metaclass=Singleton):
    """Requirements Check class."""

    def __init__(self) -> None:
        self._logger = OxtLogger(log_name=__name__)
        self._config = Config()
        self._ver_rules = VerRules()

    def check_requirements(self) -> bool:
        """
        Check requirements that have been set in file ``pyproject.toml`` in the ``tool.oxt.requirements`` section.

        Returns:
            bool: ``True`` if requirements are installed; Otherwise, ``False``.
        """
        return all(self._is_valid_version(name=name, ver=ver) == 0 for name, ver in self._config.requirements.items())

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
            self._logger.debug(f"Package {name} not installed.")
            return 2

        if not ver:
            # set default version to >=0.0.0
            ver = "==*"
        rules = self._ver_rules.get_matched_rules(ver)
        self._logger.debug(f"Found Package {name} {pkg_ver} already installed ...")
        if not rules:
            if pkg_ver:
                self._logger.info(f"Package {name} {pkg_ver} already installed, no rules")
            else:
                self._logger.error(f"Unable to find rules for {name} {ver}")
            return -1

        rules_pass = self._ver_rules.get_installed_is_valid_by_rules(rules=rules, check_version=pkg_ver)
        if rules_pass == False:
            self._logger.info(
                f"Package {name} {pkg_ver} already installed. It does not meet requirements specified by: {ver}"
            )
            return 1
        self._logger.info(f"Package {name} {pkg_ver} already installed. Requirements met for constraints: {ver}")
        return 0
