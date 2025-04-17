from __future__ import annotations
from typing import Any


class GeneralError:
    """General Error Class"""

    # all other errs should inherit from this class

    def __init__(self, error: Any = None) -> None:  # noqa: ANN401
        self._error = error

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._error})>"

    def get_error_code(self) -> int:
        return 1000

    @property
    def error(self) -> Any:  # noqa: ANN401
        return self._error
