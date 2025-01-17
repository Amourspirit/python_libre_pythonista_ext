from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, cast
import json


class PkgInstallData:
    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        self._id = kwargs.get("id", "")
        self._type_id = kwargs.get("type_id", "")
        self._package_id = kwargs.get("package_id", "")
        self._package = kwargs.get("package", "")
        self._package_version = kwargs.get("package_version", "")
        self._version = kwargs.get("version", "")
        self._data = kwargs.get("data", {})

    def save(self, path: Path) -> None:
        with path.open("w") as f:
            json.dump(self._data, f)

    def get_files(self, key: str) -> List[str]:
        return self._data.get(key, [])

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
    def data(self) -> dict:
        return self._data

    @property
    def new_dirs(self) -> List[str]:
        return self.get_files("new_dirs")

    @property
    def new_files(self) -> List[str]:
        return self.get_files("new_files")
