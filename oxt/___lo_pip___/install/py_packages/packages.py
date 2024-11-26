from __future__ import annotations
from typing import List, Dict


from .py_package import PyPackage
from .package_config import PackageConfig
from .lp_editor_package_config import LpEditorPackageConfig
from ...config import Config
from ...oxt_logger import OxtLogger


class Packages:
    """Manages rules for Python Packages"""

    def __init__(self) -> None:
        """
        Initialize PackageRules
        """
        self._config = Config()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._packages: List[PyPackage] = []
        self._load_packages()

    def _load_packages(self) -> None:
        """
        Load rules from config
        """

        def is_valid(rule: PyPackage) -> bool:
            if self._config.is_flatpak:
                if rule.is_ignored_platform("flatpak"):
                    self._log.debug("%s is ignored for flatpak", rule.name)
                    return False
                else:
                    self._log.debug("%s is valid for flatpak", rule.name)
            else:
                self._log.debug("Not flatpak")

            if self._config.is_snap:
                if rule.is_ignored_platform("snap"):
                    self._log.debug("%s is ignored for snap}", rule.name)
                    return False
                else:
                    self._log.debug("%s is valid for snap}", rule.name)
            else:
                self._log.debug("Not snap")

            if rule.is_platform("all"):
                return True

            if self._config.is_win:
                os_name = "win"
            elif self._config.is_mac:
                os_name = "mac"
            else:
                os_name = "linux"
            return rule.is_platform(os_name)

        pkg_cfg = PackageConfig()
        for rule in pkg_cfg.py_packages:
            gi = PyPackage.from_dict(**rule)
            if is_valid(gi):
                self._log.debug("Adding rule: %s}", gi)
                self.add_pkg(gi)
            else:
                self._log.debug("Ignoring rule: %s}", gi)

        if self._config.lp_settings.experimental_editor:
            lp_cfg = LpEditorPackageConfig()
            for rule in lp_cfg.py_packages:
                gi = PyPackage.from_dict(**rule)
                if is_valid(gi):
                    self._log.debug("Adding rule: %s}", gi)
                    self.add_pkg(gi)
                else:
                    self._log.debug("Ignoring rule: %s}", gi)

    def __len__(self) -> int:
        return len(self._packages)

    def __contains__(self, pkg: PyPackage) -> bool:
        return pkg in self._packages

    # region Methods

    def get_index(self, pkg: PyPackage) -> int:
        """
        Get index of Package

        Args:
            pkg (PyPackage): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._packages.index(pkg)

    def add_pkg(self, pkg: PyPackage) -> None:
        """
        Add Package

        Args:
            pkg (PyPackage): Rule to register
        """
        with self._log.indent(True):
            if pkg in self._packages:
                self._log.debug("add_pkg() Rule Already added: %s", pkg)
                return
            self._log.debug("add_pkg() Adding Rule %s", self.__class__.__name__, pkg)
            self._add_pkg(pkg=pkg)

    def remove_package(self, pkg: PyPackage):
        """
        Removes Package

        Args:
            pkg (PyPackage): pkg to remove

        Raises:
            ValueError: If an error occurs
        """
        with self._log.indent(True):
            try:
                self._packages.remove(pkg)
                self._log.debug("remove_package() Removed rule: %s,", pkg)
            except ValueError as e:
                msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
                self._log.error(msg)
                raise ValueError(msg) from e

    def _add_pkg(self, pkg: PyPackage):
        self._packages.append(pkg)

    def __repr__(self) -> str:
        return "<Packages()>"

    def to_dict(self) -> Dict[str, str]:
        """
        Convert to dict with Name as key, restriction and version as value.


        Returns:
            dict: Dict representation of the object such as ``{"verr": ">=1.0.0", "requests": "==2.0.0"}``
        """
        result = {}
        for pkg in self.packages:
            result[pkg.name] = f"{pkg.restriction}{pkg.version}"
        return result

    # endregion Methods

    # region Properties
    @property
    def packages(self) -> List[PyPackage]:
        """
        Get all rules

        Returns:
            List[PyPackage]: List of all rules
        """
        return self._packages

    # endregion Properties
