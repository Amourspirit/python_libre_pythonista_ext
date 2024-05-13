from __future__ import annotations
import os
import sys
import shutil
from typing import Set, cast, List
from pathlib import Path

import toml
from ..meta.singleton import Singleton
from ..config import Config
from .. import file_util


class Packages(metaclass=Singleton):
    """Singleton Class the Packages."""

    def __init__(self) -> None:
        self._config = Config()
        self._pkg_names = self._get_package_names()
        self._pkg_files = self._get_package_files()
        self._venv_path = Path(self._get_virtual_env_path())
        major, minor, *_ = sys.version_info
        self._site_packages_path = self._venv_path / "lib" / f"python{major}.{minor}" / "site-packages"
        if not self._site_packages_path.exists():
            # windows
            self._site_packages_path = self._venv_path / "Lib" / "site-packages"
        if not self._site_packages_path.exists():
            raise FileNotFoundError("Unable to get Site Packages Path")

    # region Methods

    def _get_package_names(self) -> Set[str]:
        """Gets the Package Names."""
        # sourcery skip: class-extract-method
        cfg = toml.load(self._config.toml_path)
        lst = cast(List[str], cfg["tool"]["oxt"]["config"]["py_pkg_names"])
        if not isinstance(lst, list):
            raise ValueError("py_pkg_names is not a list")
        self._check_list_values_are_strings(lst)
        pkg_names: Set[str] = set(lst)
        return pkg_names

    def _get_package_files(self) -> Set[str]:
        """Gets the Package Files."""
        cfg = toml.load(self._config.toml_path)
        lst = cast(List[str], cfg["tool"]["oxt"]["config"]["py_pkg_files"])
        if not isinstance(lst, list):
            raise ValueError("py_pkg_files is not a list")
        self._check_list_values_are_strings(lst)
        pkg_files: Set[str] = set(lst)
        return pkg_files

    def _check_list_values_are_strings(self, lst: List[str]) -> None:
        """Check that all the values in the list are strings."""
        for item in lst:
            if not isinstance(item, str):
                raise ValueError(f"item '{item}' is not a string")

    def _get_virtual_env_path(self) -> str:
        """
        Gets the Virtual Environment Path

        Returns:
            str: Virtual Environment Path
        """
        s_path = os.environ.get("VIRTUAL_ENV", None)
        if s_path is not None:
            return s_path
        raise FileNotFoundError("Unable to get Virtual Environment Path")

    def copy_packages(self, dst: str | Path) -> None:
        """Copies the packages to the build directory."""
        if not self._pkg_names:
            return
        dest = Path(dst) if isinstance(dst, str) else dst
        if not dest.exists():
            dest.mkdir(parents=True)

        for pkg_name in self._pkg_names:
            shutil.copytree(src=self.site_packages_path / pkg_name, dst=dest / pkg_name)

    def copy_files(self, dst: str | Path) -> None:
        """Copies the files to the build directory."""
        if not self._pkg_files:
            return
        dest = Path(dst) if isinstance(dst, str) else dst
        if not dest.exists():
            dest.mkdir(parents=True)

        for pkg_file in self._pkg_files:
            shutil.copy(src=self.site_packages_path / pkg_file, dst=dest / pkg_file)

    def clear_cache(self, dst: str | Path) -> None:
        """
        Recursively removes generic `__pycache__` .

        The `__pycache__` files are automatically created by python during the simulation.
        This function removes the generic files on simulation start and simulation end.
        """
        file_util.clear_cache(dst)

    def has_modules(self) -> bool:
        """Returns True if the packages has modules."""
        return len(self._pkg_names) + len(self._pkg_files) > 0

    # endregion Methods

    # region Properties
    @property
    def venv_path(self) -> Path:
        """The Virtual Environment Path."""
        return self._venv_path

    @property
    def site_packages_path(self) -> Path:
        """The Site Packages Path."""
        return self._site_packages_path

    @property
    def pkg_names(self) -> Set[str]:
        """The Package Names."""
        return self._pkg_names

    @property
    def pkg_files(self) -> Set[str]:
        """The Package Files."""
        return self._pkg_files

    # endregion Properties
