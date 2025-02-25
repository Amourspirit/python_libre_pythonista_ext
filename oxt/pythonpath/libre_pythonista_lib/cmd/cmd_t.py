from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdT(Protocol):
    def execute(self) -> None:  # noqa: ANN401
        ...

    def undo(self) -> None:  # noqa: ANN401
        ...

    @property
    def success(self) -> bool: ...

    @success.setter
    def success(self, value: bool) -> None: ...

    @property
    def kind(self) -> CalcCmdKind: ...

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None: ...
