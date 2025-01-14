from __future__ import annotations
import re
from typing import List, cast
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


# https://www.darius.page/pipdev

# MUST NOT be used with a single segment version number such as ~=1.
# https://peps.python.org/pep-0440/#compatible-release


class TildeEq(VerRuleBase):
    """
    A class to represent a tilde version.

    A compatible release clause consists of the compatible release operator ``~=`` and a version identifier.

    Tilde requirements specify a minimal version with some ability to update.
    If you specify a major, minor, and patch version or only a major and minor version, only patch-level changes are allowed.
    If you only specify a major version, then minor- and patch-level changes are allowed.
    """

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        v_len = len(self.vstr)
        if v_len < 3:
            return False
        if not self.vstr.startswith("~="):
            return False
        if not self._starts_with_digits_dot(self.vstr[2:].lstrip()):
            return False
        try:
            versions = self.get_versions()
            if not len(versions) == 2:
                return False
            v1 = versions[0]
            if not v1.version_parts.has_minor:
                return False
            return True
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""
        # Single digit version is not valid such as ~=1
        # All version that start with ~= will have a ending version that ends with post# where # is a number.

        ver = self.vstr[2:].strip()
        if ver == "":
            return []
        if not self._starts_with_digits_dot(ver):
            return []

        chk_ver = ReqVersion(f"=={ver}")
        vp = chk_ver.version_parts

        if vp.has_minor and vp.has_micro:
            # ~=3.1.2    >=3.1.2 <3.2.0
            v1 = ReqVersion(f">={ver}")
            v2 = ReqVersion(f"<{v1.major}.{v1.minor + 1}.0")
            return [v1, v2]

        # Version string must have at least a minor version to be valid.
        # ~=3.1a1: version 3.1a1 or later, but not version 4.0.0 or later.
        # ~=2.2: version 2.2.0 or later, but not version 3.0.0 or later.
        v1 = chk_ver.copy(prefix=">=")
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
        return self.get_version_is_valid(check_version) == 0
