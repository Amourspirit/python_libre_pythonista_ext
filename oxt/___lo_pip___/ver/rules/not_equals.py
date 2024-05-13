from __future__ import annotations
from typing import List
import re
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


class NotEquals(VerRuleBase):
    """
    A class to represent a Not Equal version.
    """

    def _starts_with_not_equal(self, string: str) -> bool:
        """Check if a string starts with != or <> followed by a space or an integer.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.

        Example:

            .. code-block:: python

                >>> self._starts_with_not_equal("!= 1")
                True
                >>> self._starts_with_not_equal("<>  2")
                True
                >>> self._starts_with_not_equal("<a")
                False
                >>> self._starts_with_not_equal("<=1")
                False
        """
        pattern = r"^(!=|<>)\s*\d"
        return bool(re.match(pattern, string))

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        v_len = len(self.vstr)
        if v_len < 3:
            return False
        if not self._starts_with_not_equal(self.vstr):
            return False
        try:
            versions = self.get_versions()
            return len(versions) == 1
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        ver = self.vstr[2:].strip()
        return [] if ver == "" else [ReqVersion(f"!={ver}")]

    def get_versions_str(self) -> str:
        """
        Gets the list of versions as strings.
        In this case in the form of ``!= 1.2.3`` or ``<> 1.2.3``.

        Returns:
            str: The version as a string or an empty string if the version is invalid.
        """
        versions = self.get_versions()
        return versions[0].get_pip_ver_str() if len(versions) == 1 else ""

    def get_version_is_valid(self, check_version: str) -> int:
        """
        Check if the version is valid. check_version is valid if it is not equal.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).

        Returns:
            int: ``0`` if the check_version is not equal, ``2`` if the check_version is equal.
                ``-2`` if the version is invalid.
        """
        try:
            check_ver = ReqVersion(f"=={check_version}")
            versions = self.get_versions()
            if len(versions) != 1:
                return -2
            v1 = versions[0]
            return 2 if check_ver == v1 else 0
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
