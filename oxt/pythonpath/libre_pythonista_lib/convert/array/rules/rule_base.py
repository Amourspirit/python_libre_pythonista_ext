from __future__ import annotations
from typing import Any


class RuleBase:
    def __init__(self) -> None:
        pass

    def get_is_match(self, value: Any) -> bool:  # noqa: ANN401
        raise NotImplementedError

    def convert(self, value: Any) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}()>"
