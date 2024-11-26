from __future__ import annotations

from .package_config import PackageConfig


class LpEditorPackageConfig(PackageConfig):
    def _get_packages_name(self) -> str:
        return "lp_editor_py_packages"
