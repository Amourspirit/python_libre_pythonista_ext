from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryT(Protocol):
    def execute(self) -> Any:  # noqa: ANN401
        ...

    @property
    def kind(self) -> CalcQryKind: ...
