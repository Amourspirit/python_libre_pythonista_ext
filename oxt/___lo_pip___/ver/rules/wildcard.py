from __future__ import annotations
from typing import List
import re
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


class Wildcard(VerRuleBase):
    """
    A class to represent a Wildcard version.

    Wildcard requirements allow for the latest (dependency dependent) version where the wildcard is positioned.
    """

    def _starts_with_equal(self, string: str) -> bool:
        """Check if a string starts with == followed by a space or an integer.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.

        Example:

            .. code-block:: python

                >>> self._starts_with_equal("== 1")
                True
                >>> self._starts_with_equal("==  2")
                True
                >>> self._starts_with_equal("<a")
                False
                >>> self._starts_with_equal("<=1")
                False
        """
        pattern = r"^==\s*"
        return bool(re.match(pattern, string))

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        vl_en = len(self.vstr)
        if vl_en == 0:
            return False
        if not self._starts_with_equal(self.vstr):
            return False
        if not self.vstr.endswith("*"):
            return False
        try:
            versions = self.get_versions()
            return len(versions) >= 1
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""

        ver = self.vstr[2:].strip()  # remove ==

        if ver[:-1].strip() == "":
            return [ReqVersion(">=0.0.0")]
        ver = ver[:-2]  # remove .*
        v1 = ReqVersion(f">={ver}")
        if v1.minor > 0:
            v2 = ReqVersion(f"<{v1.major}.{v1.minor + 1}.0")
        else:
            v2 = ReqVersion(f"<{v1.major + 1}.0.0")
        return [v1, v2]

    def get_versions_str(self) -> str:
        """Get the list of versions as strings."""
        versions = self.get_versions()
        if len(versions) == 1:
            return versions[0].get_pip_ver_str()
        if len(versions) != 2:
            return ""
        v1 = versions[0]
        v2 = versions[1]
        return f"{v1.get_pip_ver_str()}, {v2.get_pip_ver_str()}"

    def get_version_is_valid(self, check_version: str) -> int:
        """
        Check if the version is valid.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).

        Returns:
            int: ``-1`` if the version is less than the range, ``0`` if the version is in the range, ``1`` if the version is greater than the range.
                ``-2`` if the version is invalid.
        """
        try:
            check_ver = ReqVersion(f"=={check_version}")
            versions = self.get_versions()
            if len(versions) == 1:
                # in this instance a single version is returned, with a value of >=0.0.0
                return 0
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
