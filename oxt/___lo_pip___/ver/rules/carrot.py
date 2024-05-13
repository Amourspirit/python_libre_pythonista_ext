from __future__ import annotations
from typing import Any, List
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


class Carrot(VerRuleBase):
    """
    A class to represent a carrot version.

    Caret requirements allow SemVer compatible updates to a specified version.
    An update is allowed if the new version number does not modify the left-most non-zero digit
    in the major, minor, patch grouping.
    """

    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     pass

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        v_len = len(self.vstr)
        if v_len < 2:
            return False
        # return vstr.startswith("^")
        if not self.vstr.startswith("^"):
            return False
        try:
            versions = self.get_versions()
            return len(versions) == 2
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""
        ver = self.vstr[1:].strip()
        if ver == "":
            return []
        v1 = ReqVersion(f">={ver}")
        v2 = ReqVersion(f"<{v1.major + 1}.0.0")
        return [v1, v2]

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
        Check if the version is valid.

        Args:
            check_version (str): Version to check in the form of ``1.2.3`` (no prefix).
            vstr (str): version string in the form of ``^1.2.3``.

        Returns:
            int: ``-1`` if the version is less than the range, ``0`` if the version is in the range, ``1`` if the version is greater than the range.
                ``-2`` if the version is invalid.
        """
        try:
            check_ver = ReqVersion(f"=={check_version}")
            versions = self.get_versions()
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
        return self.get_version_is_valid(check_version) >= 0
