from __future__ import annotations

from .progress_dialog import ProgressDialog


class ProgressDialogTrue(ProgressDialog):
    """A progress dialog rule."""

    def get_is_match(self) -> bool:
        """Check if the terminal is a match"""
        # if window has started then a progress dialog can be shown.
        return True
