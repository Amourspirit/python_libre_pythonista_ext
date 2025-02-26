from __future__ import annotations
from typing import Any, TypeVar, Generic, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

TResult = TypeVar("TResult", covariant=True)


class QryT(Protocol[TResult]):
    """A generic Protocol for queries that return a result of type TResult."""

    def execute(self) -> TResult: ...

    @property
    def kind(self) -> CalcQryKind: ...

    @kind.setter
    def kind(self, value: CalcQryKind) -> None: ...
