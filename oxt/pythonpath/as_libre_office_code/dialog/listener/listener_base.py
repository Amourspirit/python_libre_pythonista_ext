from __future__ import annotations
from typing import Generic, TypeVar
import uno
import unohelper

T = TypeVar("T")


class ListenerBase(unohelper.Base, Generic[T]):
    def __init__(self, component: T):
        self._component = component

    def disposing(self, source):
        self._component = None

    @property
    def component(self) -> T:
        return self._component  # type: ignore
