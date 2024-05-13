from __future__ import annotations
import shutil

from ..meta.singleton import Singleton
from ..processing.pre_packages_pure import PrePackagesPure
from .pip_install_build import PipInstallBuild
from ..processing.pre_packages_pure import PrePackagesPure
from ..config import Config
from .. import file_util


class PreInstallPure(metaclass=Singleton):
    """
    Reads values from pyproject.toml and downloads the required files and installs them into the build pythonpath folder.

    All the files are expected to be pure python files.
    """

    def __init__(self) -> None:
        self._pre_packages = PrePackagesPure()
        self._config = Config()
        self._build_path = self._config.root_path / self._config.build_dir_name
        if self._config.zip_preinstall_pure:
            self._dst = self._build_path / "pure"
        else:
            self._dst = self._build_path / "pythonpath"

    def install(self) -> None:
        """Install the packages."""
        for pkg, ver in self._pre_packages.packages.items():
            pip_install = PipInstallBuild(pkg, ver)
            pip_install.install()
        self._clear_cache()
        self._zip_pure()

    def _zip_pure(self) -> None:
        """Zip the pure python packages."""
        if not self._config.zip_preinstall_pure:
            return
        if not self._dst.exists():
            return
        file_util.zip_folder(folder=self._dst)
        shutil.rmtree(self._dst)

    def _clear_cache(self) -> None:
        """
        Recursively removes generic `__pycache__` .

        The `__pycache__` files are automatically created by python during the simulation.
        This function removes the generic files on simulation start and simulation end.
        """
        if not self._dst.exists():
            return
        file_util.clear_cache(self._dst)
