from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, cast
import json


class PkgInstallData:
    class PkgData:
        def __init__(self) -> None:
            self.new_dirs: List[str] = []
            self.new_files: List[str] = []
            self.new_bin_files: List[str] = []
            self.new_lib_files: List[str] = []
            self.new_inc_files: List[str] = []

        @classmethod
        def from_dict(cls, data: Dict[str, str]) -> PkgInstallData.PkgData:
            obj = cls()
            obj.new_dirs.extend(data.get("new_dirs", []))
            obj.new_files.extend(data.get("new_files", []))
            obj.new_bin_files.extend(data.get("new_bin_files", []))
            obj.new_lib_files.extend(data.get("new_lib_files", []))
            obj.new_inc_files.extend(data.get("new_inc_files", []))
            return obj

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        self._id = kwargs.get("id", "")
        self._type_id = kwargs.get("type_id", "")
        self._package_id = kwargs.get("package_id", "")
        self._package = kwargs.get("package", "")
        self._package_version = kwargs.get("package_version", "")
        self._version = kwargs.get("version", "")
        data = kwargs.get("data", {})
        self._data = PkgInstallData.PkgData.from_dict(data)

    def save(self, path: Path) -> None:
        with path.open("w") as f:
            json.dump(self._data, f)

    @staticmethod
    def from_file(path: Path) -> PkgInstallData:
        with path.open() as f:
            return PkgInstallData(**cast(Dict[str, str], json.load(f)))

    @property
    def id(self) -> str:
        return self._id

    @property
    def type_id(self) -> str:
        return self._type_id

    @property
    def package_id(self) -> str:
        return self._package_id

    @property
    def package(self) -> str:
        return self._package

    @property
    def package_version(self) -> str:
        return self._package_version

    @property
    def version(self) -> str:
        return self._version

    @property
    def data(self) -> PkgData:
        return self._data
