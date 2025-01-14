from __future__ import annotations
import re


class VerRuleBase:
    """
    A class to represent a version rule.
    """

    def __init__(self, vstr: str) -> None:
        self._vstr = vstr

    def extract_suffix(self, ver_str: str) -> str:
        """
        Extracts the suffix part of a string, assuming the suffix is non-numeric.

        Args:
            string: The input string.

        Returns:
            The suffix part of the string, or empty string if no suffix is found.
        """

        parts = ver_str.split(".")
        parts.reverse()
        last_part = parts[0]  # type: ignore
        if not last_part.isdigit():
            return last_part
        return ""

    def _starts_with_digits_dot_or_digit_only(self, string: str) -> bool:
        """Test if a string starts with one or more digits followed by a dot or is a single number.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.
        """
        pattern = r"^\d+\."
        return string.isdigit() or bool(re.match(pattern, string))

    def _starts_with_digits_dot(self, string: str) -> bool:
        """Test if a string starts with one or more digits followed by a dot.

        Args:
            string (str): The input string.

        Returns:
            bool: True if the string matches the pattern, False otherwise.
        """
        pattern = r"^\d+\."
        return bool(re.match(pattern, string))

    @property
    def vstr(self) -> str:
        """Get the version string."""
        return self._vstr
