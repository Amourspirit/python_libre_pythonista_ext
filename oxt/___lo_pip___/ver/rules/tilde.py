from __future__ import annotations
import re
from typing import List, cast
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase


# https://www.darius.page/pipdev

# MUST NOT be used with a single segment version number such as ~=1.
# https://peps.python.org/pep-0440/#compatible-release


class Tilde(VerRuleBase):
    """
    A class to represent a tilde version.

    Tilde requirements specify a minimal version with some ability to update.
    If you specify a major, minor, and patch version or only a major and minor version, only patch-level changes are allowed.
    If you only specify a major version, then minor- and patch-level changes are allowed.
    """

    def _starts_with_digits_and_dot(self, string: str) -> bool:
        """Test if a string starts with one or more digits followed by a dot.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.
        """
        pattern = r"^\d+\."
        return bool(re.match(pattern, string))

    def get_is_match(self) -> bool:
        """Check if the version matches the given string."""
        v_len = len(self.vstr)
        if v_len < 3:
            return False
        if not self.vstr.startswith("~="):
            return False
        if not self._starts_with_digits_and_dot(self.vstr[2:].lstrip()):
            return False
        try:
            versions = self.get_versions()
            return len(versions) == 2
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""
        # Single digit version is not valid such as ~=1
        # All version that start with ~= will have a ending version that ends with post# where # is a number.

        ver = self.vstr[2:].strip()
        if ver == "":
            return []
        if not self._starts_with_digits_and_dot(ver):
            return []
        v1 = ReqVersion(f">={ver}")
        if v1.micro > 0 or v1.minor > 0:
            v2 = ReqVersion(f"<{v1.major}.{v1.minor + 1}.0")
        else:
            v2 = ReqVersion(f"<{v1.major + 1}.0.0")
        return [v1, v2]

    # def _get_v2(self, v1: ReqVersion) -> ReqVersion:
    #     """Get the second version."""
    #     # second version will end with post# where # is a number.
    #     # if version is 'a' or 'dev' or 'post' or 'rc' or 'pre' then the post
    #     # number will be increased by one.
    #     # Example:
    #     #   ~=1.2.3a1 -> 1.2.4.post2
    #     #   ~=1.2dev3 -> 1.3.1.post4
    #     #   ~=1.2rc5 -> 1.3.1.post6

    #     post_int = 1
    #     if v1.pre is not None:
    #         post_int = v1.pre[1] + 1
    #     elif v1.post is not None:
    #         post_int = v1.post + 1
    #     elif v1.dev is not None:
    #         post_int = v1.dev + 1

    #     if v1.micro > 0:
    #         vstr = f"<{v1.major}.{v1.minor + 1}"
    #     elif v1.minor > 0:
    #         vstr = f"<{v1.major}.{v1.minor + 1}"
    #     else:
    #         return ReqVersion(f"<{v1.major + 1}.0.0")

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
