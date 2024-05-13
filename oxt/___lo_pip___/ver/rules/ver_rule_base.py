from __future__ import annotations
from ..req_version import ReqVersion
from typing import Any, List


class VerRuleBase:
    """
    A class to represent a version rule.
    """

    def __init__(self, vstr: str) -> None:
        self._vstr = vstr

    @property
    def vstr(self) -> str:
        """Get the version string."""
        return self._vstr
