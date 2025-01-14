from __future__ import annotations
from typing import Any, List
from ..req_version import ReqVersion
from .ver_rule_base import VerRuleBase

# see: https://python-poetry.org/docs/dependency-specification/


class Carrot(VerRuleBase):
    """
    A class to represent a carrot version.

    Caret requirements allow SemVer compatible updates to a specified version.
    An update is allowed if the new version number does not modify the left-most non-zero digit
    in the major, minor, patch grouping.

    Note:
        The caret requirement is specified with a leading ``^`` character.

        -``^1.2.3`` is ``>=1.2.3 <2.0.0``
        - ``^1.2`` is ``>=1.2.0 <2.0.0``
        - ``^1`` is ``>=1.0.0 <2.0.0``
        - ``^0.2.3`` is ``>=0.2.3 <0.3.0``
        - ``^0.0.3`` is ``>=0.0.3 <0.0.4``
        - ``^0.0`` is ``>=0.0.0 <0.1.0``
        - ``^0`` is ``>=0.0.0 <1.0.0``
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
            ver = self.vstr[1:].strip()
            suffix = self.extract_suffix(ver)
            if suffix:
                # carrot does not support suffixes
                return False
            versions = self.get_versions()
            return len(versions) == 2
        except Exception:
            return False

    def get_versions(self) -> List[ReqVersion]:
        """Get the list of versions."""
        ver = self.vstr[1:].strip()
        if ver == "":
            return []

        chk_ver = ReqVersion(f"=={ver}")
        vp = chk_ver.version_parts

        if vp.has_minor and vp.has_micro:
            # ^1.2.3    >=1.2.3 <2.0.0
            v1 = ReqVersion(f">={ver}")
            if chk_ver.major == 0 and chk_ver.minor == 0:
                # ^0.0.3	>=0.0.3 <0.0.4
                v2 = ReqVersion(f"<0.0.{chk_ver.micro + 1}")
            elif chk_ver.major == 0:
                # ^0.2.3	>=0.2.3 <0.3.0
                v2 = ReqVersion(f"<0.{chk_ver.minor + 1}.0")
            else:
                v2 = ReqVersion(f"<{v1.major + 1}.0.0")
            return [v1, v2]

        if vp.has_minor:
            if chk_ver.major == 0 and chk_ver.minor == 0:
                # ^0.0      >=0.0.0 <0.1.0
                v1 = ReqVersion(">=0.0.0")
                v2 = ReqVersion("<0.1.0")
            else:
                # ^1.2      >=1.2.0 <2.0.0
                v1 = ReqVersion(f">={chk_ver.major}.{chk_ver.minor}.0")
                v2 = ReqVersion(f"<{v1.major + 1}.0.0")
            return [v1, v2]

        if chk_ver.major == 0:
            # ^0    >=0.0.0 <1.0.0
            v1 = ReqVersion(">=0.0.0")
            v2 = ReqVersion("<1.0.0")
        else:
            # ^1   >=1.0.0 <2.0.0
            v1 = ReqVersion(f">={chk_ver.major}.0.0")
            v2 = ReqVersion(f"<{v1.major + 1}.0.0")

        # if suffix:
        #     v_first = ReqVersion(f">={chk_ver.major}.0.0")

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
