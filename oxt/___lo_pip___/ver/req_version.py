from __future__ import annotations
from packaging.version import Version
import re


class ReqVersion(Version):
    """A class to represent a version requirement."""

    def __init__(self, version: str) -> None:
        """Initialize a Version object.

        Args:
            version (str): The string representation of a version which will be parsed and normalized
                before use.

        Raises:
            InvalidVersion: If the ``version`` does not conform to PEP 440 in any way then this exception will be raised.
        """
        ver = self._process_full_version(version)
        super().__init__(ver)

    def __repr__(self) -> str:
        """A representation of the ReqVersion that shows all internal state.

        >>> ReqVersion('1.0.0')
        <ReqVersion('1.0.0')>
        """
        return f"<ReqVersion('{self}')>"

    def _process_full_version(self, version: str) -> str:
        if match := re.search(r"\d", version):
            prefix = version[: match.start()].strip() or "=="
            ver = version[match.start() :].strip()
        else:
            # no prefix means equal.
            prefix = "=="
            ver = version.strip()
        if not self._validate_prefix(prefix):
            raise ValueError(f"Invalid prefix: {prefix}")
        self._prefix = prefix
        return ver

    def _validate_prefix(self, prefix: str) -> bool:
        return prefix in {"==", "!=", "<>", "<", "<=", ">", ">="} if prefix else True

    def get_ver_is_valid(self, version: str) -> bool:
        """Check if the version is valid."""
        ver = Version(version)
        if self._prefix == "==":
            return ver == self
        if self._prefix == "!=":
            return ver != self
        if self._prefix == "<":
            return ver < self
        if self._prefix == "<=":
            return ver <= self
        if self._prefix == ">":
            return ver > self
        return ver >= self if self._prefix == ">=" else False

    def get_pip_ver_str(self) -> str:
        """Get the pip version string."""
        return self._prefix + str(self)
        # return f"{self._prefix} {self.major}.{self.minor}.{self.micro}"

    @property
    def prefix(self) -> str:
        """Get the prefix such as ``==`` or ``>=``."""
        return self._prefix
