from __future__ import annotations
from typing import Generic, TypeVar, TYPE_CHECKING
import uno
import unohelper

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject

T = TypeVar("T")


class ListenerBase(unohelper.Base, Generic[T]):
    def __init__(self, component: T):
        self._component = component

    def disposing(self, Source: EventObject):
        self._component = None

    @property
    def component(self) -> T:
        return self._component  # type: ignore
