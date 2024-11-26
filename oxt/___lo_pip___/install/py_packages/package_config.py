from __future__ import annotations
from pathlib import Path
from typing import Dict, List
import json

from ...basic_config import BasicConfig


class PackageConfig:
    def __init__(self) -> None:
        self._config = BasicConfig()
        lo_pip = self._config.lo_pip_dir
        if not lo_pip:
            raise ValueError("lo_pip not found in config.json")
        root = self._find_lo_pip_dir(lo_pip)

        config_file = Path(root, "config.json")
        with open(config_file, "r") as file:
            data = json.load(file)

        self._py_packages = data.get(self._get_packages_name(), [])

    def _find_lo_pip_dir(self, lp_pip: str) -> Path:
        current_dir = Path(__file__).parent
        while current_dir != current_dir.root:
            if (current_dir / lp_pip).is_dir():
                return current_dir / lp_pip
            current_dir = current_dir.parent
        raise FileNotFoundError(f"Directory '{lp_pip}' not found")

    def _get_packages_name(self) -> str:
        return "py_packages"

    # region Properties
    @property
    def py_packages(self) -> List[Dict[str, str]]:
        return self._py_packages

    # endregion Properties
