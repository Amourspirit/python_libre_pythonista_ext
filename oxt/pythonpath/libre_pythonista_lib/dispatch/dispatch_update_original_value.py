from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.calc import CalcDoc
from ooodev.io.log import logging as logger


if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener


class DispatchUpdateOriginalValue(unohelper.Base, XDispatch):
    def __init__(self, sheet: str, cell: str):
        self._sheet = sheet
        self._cell = cell

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        pass

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        doc = CalcDoc.from_current_doc()
        sheet = doc.sheets[self._sheet]
        cell = sheet[self._cell]
        if cell.has_custom_property("OriginalValue"):
            cell.set_custom_property("OriginalValue", cell.value)
            logger.debug(f"Cell {self._cell} Original value has been updated to the current value of {cell.value}.")
        else:
            logger.error(f"Cell {self._cell} does not have OriginalValue custom property.")

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        pass
