from __future__ import annotations
from typing import List
import re
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


class Lesser(VerRuleBase):
    """
    A class to represent a Less than version.
    """

    def _starts_with_greater_than(self, string: str) -> bool:
        """Check if a string starts with < followed by a space or an integer.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.

        Example:

            .. code-block:: python

                >>> self._starts_with_greater_than("< 1")
                True
                >>> self._starts_with_greater_than("<  2")
                True
                >>> self._starts_with_greater_than("<a")
                False
                >>> self._starts_with_greater_than("<=1")
                False
        """
        pattern = r"^<\s*\d"
        return bool(re.match(pattern, string))

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        v_len = len(self.vstr)
        if v_len < 2:
            return False
        if not self._starts_with_greater_than(self.vstr):
            return False
        try:
            versions = self.get_versions()
            return len(versions) == 1
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        ver = self.vstr[1:].strip()
        return [] if ver == "" else [ReqVersion(f"<{ver}")]

    def get_versions_str(self) -> str:
        """Get the list of versions as strings."""
        versions = self.get_versions()
        return versions[0].get_pip_ver_str() if len(versions) == 1 else ""

    def get_version_is_valid(self, check_version: str) -> int:
        """
        Check if the version is valid. check_version is valid if it is less.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).

        Returns:
            int: ``0`` if the check_version is less than, ``1`` if the check_version is greater.
                ``2`` if versions are equal. ``-2`` if the version is invalid.
        """
        try:
            check_ver = ReqVersion(f"=={check_version}")
            versions = self.get_versions()
            if len(versions) != 1:
                return -2
            v1 = versions[0]
            if check_ver < v1:
                return 0
            elif check_ver > v1:
                return 1
            else:
                # equal
                return 2
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
