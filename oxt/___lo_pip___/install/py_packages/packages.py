from __future__ import annotations
from typing import List, Dict
import sys

from .py_package import PyPackage
from .package_config import PackageConfig
from .lp_editor_package_config import LpEditorPackageConfig
from ...config import Config
from ...oxt_logger import OxtLogger
from ...ver.req_version import ReqVersion
from ...ver.rules.ver_rules import VerRules


class Packages:
    """Manages rules for Python Packages"""

    def __init__(self) -> None:
        """
        Initialize PackageRules
        """
        self._config = Config()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._packages: List[PyPackage] = []
        self._py_ver = self._get_py_ver()
        self._pkg_cfg = PackageConfig()
        self._load_packages()

    def _get_py_ver(self) -> str:
        # This is here for easier testing. It can be mocked in tests.
        return f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"

    def _load_packages(self) -> None:
        """
        Load rules from config
        """
        ver_rules = VerRules()

        def check_version_constraints(rule: PyPackage) -> bool:
            if rule.python_versions:
                self._log.debug("Checking Python version constraints for %s", rule.name)
            else:
                self._log.debug("No Python version constraints for %s", rule.name)
                return True
            current_ver = ReqVersion(self._py_ver)
            for py_ver in rule.python_versions:
                constraint_ver = ReqVersion(py_ver)
                if constraint_ver.prefix == ">":
                    if current_ver >= constraint_ver:
                        return False
                elif constraint_ver.prefix == ">=":
                    if current_ver < constraint_ver:
                        return False
                elif constraint_ver.prefix == "<":
                    if current_ver >= constraint_ver:
                        return False
                elif constraint_ver.prefix == "<=":
                    if current_ver > constraint_ver:
                        return False
                elif constraint_ver.prefix == "!=":
                    if constraint_ver == current_ver:
                        return False
                elif constraint_ver.prefix == "==":
                    if constraint_ver != current_ver:
                        return False
                else:
                    raise ValueError(f"Unsupported operator: {constraint_ver.prefix}")
            return True

        def is_valid(rule: PyPackage) -> bool:
            nonlocal ver_rules

            if check_version_constraints(rule):
                self._log.debug(
                    "is_valid() Python version %s for %s satisfies all constraints.", self._py_ver, rule.name
                )
            else:
                self._log.debug(
                    self._log.debug(
                        "is_valid() Python version %s for %s does not satisfies all constraints.",
                        self._py_ver,
                        rule.name,
                    )
                )
                return False

            if self._config.is_win:
                platform = "win"
            elif self._config.is_mac:
                platform = "mac"
            elif self._config.is_flatpak:
                platform = "flatpak"
            elif self._config.is_snap:
                platform = "snap"
            else:
                platform = "linux"
            if rule.is_ignored_platform(platform):
                self._log.debug(
                    "is_valid() Package %s not valid for platform %s. Ignored platform", rule.name, platform
                )
                return False
            if rule.is_platform(platform):
                self._log.debug("is_valid() Package %s valid for platform %s", rule.name, platform)
                return True
            self._log.debug("is_valid() Package %s not valid for platform %s", rule.name, platform)
            return False

        for rule in self._pkg_cfg.py_packages:
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
        if pkg in self._packages:
            self._log.debug("add_pkg() Rule Already added: %s", pkg)
            return
        self._log.debug("add_pkg() Adding Rule %s", pkg)
        self._add_pkg(pkg=pkg)

    def remove_package(self, pkg: PyPackage) -> None:
        """
        Removes Package

        Args:
            pkg (PyPackage): pkg to remove

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._packages.remove(pkg)
            self._log.debug("remove_package() Removed rule: %s,", pkg)
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            self._log.error(msg)
            raise ValueError(msg) from e

    def _add_pkg(self, pkg: PyPackage) -> None:
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

    def get_all_packages(self, all_pkg: bool = False, include_non_removable_packages: bool = False) -> List[PyPackage]:
        """
        Gets all packages from the config.
        Args:
            all_pkg (bool, optional): Include all packages. Defaults to False.
                When True, all packages are included. When False, only ``py_packages`` and ``requirements`` are included.
            include_non_removable_packages (bool, optional): Include packages that are not removable. Defaults to False.
                In the config this would be the values for ``no_pip_remove``.

        Returns:
            List[PyPackage]: List of all Packages

        Note:
            ``lp_editor_py_packages`` are only included when ``all_pkg`` is True.
        """

        def make_pkg(name: str, constraint: str) -> PyPackage:
            ver = ReqVersion(constraint, ">=")
            return PyPackage(name=name, version=str(ver), restriction=ver.prefix, platform=("all",))

        pkgs = []
        for pkg in self.packages:
            if all_pkg:
                pkgs.append(pkg.copy())
            else:
                if pkg.pkg_type == "py_packages":
                    pkgs.append(pkg.copy())

        for key, value in self._config.requirements.items():
            if include_non_removable_packages:
                pkgs.append(make_pkg(key, value))
            else:
                if key not in self._config.no_pip_remove:
                    pkgs.append(make_pkg(key, value))
        return pkgs

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
