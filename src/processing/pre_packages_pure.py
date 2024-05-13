from __future__ import annotations
from typing import cast, Dict, List
import toml

from ..config import Config
from .pre_packages import PrePackages


class PrePackagesPure(PrePackages):
    """Singleton Class the Packages."""

    # region Methods Override

    def _get_package_dict(self) -> Dict[str, str]:
        """Gets the Package Names."""
        result: Dict[str, str] = {}
        cfg = toml.load(self.config.toml_path)
        if "preinstall" not in cfg["tool"]["oxt"]:
            return result
        if "pure" not in cfg["tool"]["oxt"]["preinstall"]:
            return result
        result = cast(Dict[str, str], cfg["tool"]["oxt"]["preinstall"]["pure"])
        if not isinstance(result, dict):
            raise ValueError("tool.oxt.preinstall.pure is not a dictionary")
        self._check_dict_values_are_strings(result)
        result.update(result)
        return result

    # endregion Methods Override
