from __future__ import annotations
from abc import abstractmethod
from typing import Dict, List

from ..meta.singleton import Singleton
from ..config import Config


class PrePackages(metaclass=Singleton):
    """Singleton Class the Packages."""

    def __init__(self) -> None:
        self._config = Config()
        self._pkg_dict = self._get_package_dict()

    # region Methods

    @abstractmethod
    def _get_package_dict(self) -> Dict[str, str]:
        pass

    def _check_dict_values_are_strings(self, d: Dict[str, str]) -> None:
        """Check that all the values in the list are strings."""
        for value in d.values():
            if not isinstance(value, str):
                raise ValueError(f"item '{value}' is not a string")

    def has_modules(self) -> bool:
        """Returns True if the packages has modules."""
        return len(self._pkg_dict) > 0

    # endregion Methods

    # region Properties
    @property
    def packages(self) -> Dict[str, str]:
        """The Package Dictionary."""
        return self._pkg_dict

    @property
    def config(self) -> Config:
        """The Config."""
        return self._config

    # endregion Properties
