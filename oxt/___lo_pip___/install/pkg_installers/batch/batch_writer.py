from __future__ import annotations
from typing import Iterable, TYPE_CHECKING
from ...py_packages.packages import Packages
from ....lo_util.target_path import TargetPath

if TYPE_CHECKING:
    from ..install_pkg import InstallPkg


class BatchWriter:
    def __init__(self, installer: InstallPkg) -> None:
        self._installer = installer
        self._packages = Packages()
        self._target_path = TargetPath()

    @property
    def installer(self) -> InstallPkg:
        return self._installer

    @property
    def packages(self) -> Packages:
        return self._packages

    @property
    def target_path(self) -> TargetPath:
        return self._target_path
