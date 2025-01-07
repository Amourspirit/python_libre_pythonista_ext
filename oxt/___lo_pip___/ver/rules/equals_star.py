from __future__ import annotations
from typing import Tuple
from packaging.version import Version

from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase
from typing import List
import re


class _VersionParts:
    def __init__(self, ver: str) -> None:
        """
        Initialize the version object with a version string such as ``1.*`` or ``1.2.*``.

        Args:
            ver (str): The version string to be processed.
        """

        self._ver_str = ver
        major, minor, micro = self._get_process_parts(ver)
        self._has_minor = minor >= 0
        self._has_micro = micro >= 0

        self._version_parts = (
            major,
            0 if minor < 0 else minor,
            0 if micro < 0 else micro,
        )

    def _get_process_parts(self, ver: str) -> Tuple[int, int, int]:
        # parts = ver.split(".")
        # Filter out non-numeric parts
        # numeric_parts = [part for part in parts if part.isdigit()]
        if ver.endswith(".*"):
            ver = ver[:-2].strip()

        v = Version(ver)
        numeric_parts = v.release
        if len(numeric_parts) == 2:
            return int(numeric_parts[0]), int(numeric_parts[1]), -1
        if len(numeric_parts) == 3:
            return int(numeric_parts[0]), int(numeric_parts[1]), int(numeric_parts[2])
        # if len(numeric_parts) == 1:
        return int(numeric_parts[0]), -1, -1

    def __repr__(self) -> str:
        return f"<VersionParts({self._ver_str})>"

    def __str__(self) -> str:
        return self._ver_str

    @property
    def version_parts(self) -> Tuple[int, int, int]:
        """
        Returns the version parts as a tuple of three integers.

        The parts will all be a value of ``0`` or Greater. Event if the version string did not contain a minor or micro version.

        Returns:
            Tuple[int, int, int]: A tuple containing the major, minor, and patch version numbers.
        """

        return self._version_parts

    @property
    def has_minor(self) -> bool:
        """Check if the version has a minor version."""
        return self._has_minor

    @property
    def has_micro(self) -> bool:
        """Check if the version has a micro version."""
        return self._has_micro


class EqualsStar(VerRuleBase):
    """
    A class to represent a Equal version.
    """

    def __init__(self, vstr: str) -> None:
        super().__init__(vstr)
        self._v_parts = []

    def _starts_with_equal(self, string: str) -> bool:
        """Check if a string starts with == followed by a space or an integer.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.

        Example:

            .. code-block:: python

                >>> self._starts_with_equal("== 1.*")
                True
                >>> self._starts_with_equal("==  2.1.*")
                True
                >>> self._starts_with_equal("<a")
                False
                >>> self._starts_with_equal("<=1")
                False
        """
        pattern = r"^==\s*\d"
        return bool(re.match(pattern, string))

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        if self.vstr == "==*":
            # Wildcard will handle this
            return False
        v_len = len(self.vstr)
        if v_len < 3:
            return False
        if not self._starts_with_equal(self.vstr):
            return False
        if not self.vstr.endswith("*"):
            return False
        ver = self.vstr[2:].strip()
        v_parts = ver.split(".")
        for part in v_parts[:-1]:
            if not part.isdigit():
                return False
        if v_parts[-1] != "*":
            return False
        return True

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions. In this case it will be a two versions, unless vstr is invalid in which case it will be an empty list."""
        ver = self.vstr[2:].strip()
        vp = _VersionParts(ver)
        major, minor, micro = vp.version_parts
        if vp.has_minor and vp.has_micro:
            # ==1.2.3.* -->  1.2.3, 1.2.3.post1,
            return [
                ReqVersion(f">={major}.{minor}.{micro}"),
                ReqVersion(f"<{major}.{minor}.{micro + 1}.dev1"),
            ]
        if vp.has_minor:
            # ==1.2.* -->  1.2, 1.2.post1, 1.2.1, 1.2.1.post1
            return [
                ReqVersion(f">={major}.{minor}"),
                ReqVersion(f"<{major}.{minor + 1}.dev1"),
            ]
        # ==1.* -->  1, 1.post1, 1.0.1, 1.0.1.post1, 1.1, 1.1.post1, 1.1.1, 1.1.1.post1
        return [
            ReqVersion(f">={major}"),
            ReqVersion(f"<{major+1}.dev1"),
        ]

    def get_versions_str(self) -> str:
        """Get the list of versions as strings."""
        versions = self.get_versions()
        if len(versions) != 2:
            return ""
        v1 = versions[0]
        v2 = versions[1]
        return f"{v1.get_pip_ver_str()}, {v2.get_pip_ver_str()}"

    def get_version_is_valid(self, check_version: str) -> int:
        """
        Check if the version is valid. check_version is valid if it is equal.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).

        Returns:
            int: ``0`` if the check_version is equal, ``1`` if the check_version is greater.
                ``-1`` if the check_version is less. ``-2`` if the version is invalid.
        """
        try:
            check_ver = ReqVersion(f"=={check_version}")
            versions = self.get_versions()
            if len(versions) != 2:
                return -2
            v1 = versions[0]
            v2 = versions[1]
            if check_ver >= v1 and check_ver < v2:
                return 0
            return -1 if check_ver < v1 else 1
        except Exception:
            return -2

    def get_installed_is_valid(self, check_version: str) -> bool:
        """
        Gets if the installed version is valid when compared to this rule.

        Args:
            check_version (str): The installed version to check.

        Returns:
            bool: True if the installed version is valid, False otherwise.
        """
        return self.get_version_is_valid(check_version) == 0
