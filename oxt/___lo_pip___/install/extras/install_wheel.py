"""After pip is installed this module can install Wheel."""
from __future__ import annotations
from typing import Dict
from .extra import Extra


class InstallWheel(Extra):
    """
    Installs Wheel package if it is not already installed.
    """

    def _get_packages(self) -> Dict[str, str]:
        """
        Gets the Package Names.
        """
        return {"wheel": ""}
