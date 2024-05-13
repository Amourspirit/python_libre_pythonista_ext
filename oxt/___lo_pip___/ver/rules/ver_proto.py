from __future__ import annotations
from ..req_version import ReqVersion
from typing import Protocol, List


class VerProto(Protocol):
    """A protocol for version objects."""

    def __init__(self, vstr: str) -> None:
        """Initialize the version object."""
        ...

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        ...

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""
        ...

    def get_versions_str(self) -> str:
        """Get the list of versions as strings."""
        ...

    def get_version_is_valid(self, check_version: str) -> int:
        """
        Check if the version is valid.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).

        Returns:
            Returns:
            int: ``0`` if the version is in the range, some other value if the version is not in the range.
                Implemented by each rule.
        """
        ...

    def get_installed_is_valid(self, check_version: str) -> bool:
        """
        Gets if the installed version is valid when compared to this rule.

        Args:
            check_version (str): The installed version to check.

        Returns:
            bool: True if the installed version is valid, False otherwise.
        """
        ...

    @property
    def vstr(self) -> str:
        """Get the version string."""
        ...
