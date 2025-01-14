from __future__ import annotations
from typing import Any, Tuple
from packaging.version import Version
import re

# https://packaging.pypa.io/en/stable/index.html


class VersionParts:
    def __init__(self, ver: str) -> None:
        """
        Initialize the version object with a version string such as ``1.2.3`` or ``1.2`` or ``1``.

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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts == other.version_parts
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts != other.version_parts
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts < other.version_parts
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts <= other.version_parts
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts > other.version_parts
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, VersionParts):
            return self._version_parts >= other.version_parts
        return NotImplemented

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


class ReqVersion(Version):
    """A class to represent a version requirement."""

    def __init__(self, version: str, default_prefix="==") -> None:
        """Initialize a Version object.

        Args:
            version (str): The string representation of a version which will be parsed and normalized
                before use.
            default_prefix (str, optional): The default prefix to use if none is provided. Defaults to "==".

        Raises:
            InvalidVersion: If the ``version`` does not conform to PEP 440 in any way then this exception will be raised.
        """
        self.__prefix = ""
        self.__default_prefix = default_prefix
        self.__ver = self._process_full_version(version)
        self.__version_parts = VersionParts(self.__ver)
        super().__init__(self.__ver)

    def __repr__(self) -> str:
        """A representation of the ReqVersion that shows all internal state.

        >>> ReqVersion('1.0.0')
        <ReqVersion('1.0.0')>
        """
        return f"<ReqVersion('{self}')>"

    def _process_full_version(self, version: str) -> str:
        if match := re.search(r"\d", version):
            prefix = version[: match.start()].strip() or self.__default_prefix
            ver = version[match.start() :].strip()
        else:
            # no prefix means use default.
            prefix = self.__default_prefix
            ver = version.strip()
        if not self._validate_prefix(prefix):
            raise ValueError(f"Invalid prefix: {prefix}")
        self.__prefix = prefix
        return ver

    def _validate_prefix(self, prefix: str) -> bool:
        return prefix in {"==", "!=", "<>", "<", "<=", ">", ">="} if prefix else True

    def get_ver_is_valid(self, version: str = "") -> bool:
        """
        Check if the version is valid.

        Args:
            version (str, optional): The version to check. Defaults to Version used in constructor.
        """
        if not version:
            version = self.__ver
        ver = Version(version)
        if self.__prefix == "==":
            return super().__eq__(ver)
        if self.__prefix == "!=":
            return super().__ne__(ver)
        if self.__prefix == "<":
            return super().__lt__(ver)
        if self.__prefix == "<=":
            return super().__le__(ver)
        if self.__prefix == ">":
            return super().__gt__(ver)
        if self.__prefix == ">=":
            return super().__ge__(ver)
        return False

    def get_pip_ver_str(self) -> str:
        """Get the pip version string. In the format of ``==1.0.0``."""
        return self.__prefix + str(self)
        # return f"{self._prefix} {self.major}.{self.minor}.{self.micro}"

    def copy(self, prefix="") -> ReqVersion:
        """Copy the version object."""
        if not prefix:
            prefix = self.__prefix
        return ReqVersion(f"{prefix}{self}")

    # region Comparisons
    def _compare_version(self, prefix: str, other: object) -> bool:
        if isinstance(other, (ReqVersion, Version)):
            return ReqVersion(f"{prefix}{self}").get_ver_is_valid(str(other))
        elif isinstance(other, str):
            try:
                return ReqVersion(f"{prefix}{self}").get_ver_is_valid(other)
            except Exception:
                return False
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        return self._compare_version("==", other)

    def __ne__(self, other: object) -> bool:
        return self._compare_version("!=", other)

    def __lt__(self, other: object) -> bool:
        return self._compare_version("<", other)

    def __le__(self, other: object) -> bool:
        return self._compare_version("<=", other)

    def __gt__(self, other: object) -> bool:
        return self._compare_version(">", other)

    def __ge__(self, other: object) -> bool:
        return self._compare_version(">=", other)

    # endregion

    @property
    def prefix(self) -> str:
        """Get the prefix such as ``==`` or ``>=``."""
        return self.__prefix

    @property
    def version_parts(self) -> VersionParts:
        """Get the version parts as a tuple of three integers."""
        return self.__version_parts
