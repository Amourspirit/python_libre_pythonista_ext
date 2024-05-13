from __future__ import annotations
from typing import Protocol


class ProgressT(Protocol):
    """A protocol for progress window objects."""

    def __init__(self) -> None:
        """Initialize the object."""
        ...

    def get_is_match(self) -> bool:
        """Check if the progress is a match"""
        ...

    def start(self, msg: str, title: str = "Progress") -> None:
        """Start the progress window."""
        ...

    def stop(self) -> None:
        """Stop the progress window."""
        ...
