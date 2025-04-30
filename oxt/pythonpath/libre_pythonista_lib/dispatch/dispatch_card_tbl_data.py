from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.calc import CalcDoc
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from oxt.pythonpath.libre_pythonista_lib.dialog.card.tbl_data_card2 import TblDataCard2
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.dialog.card.tbl_data_card2 import TblDataCard2
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.log.log_mixin import LogMixin


class DispatchCardTblData(XDispatch, LogMixin, EventsPartial, unohelper.Base):
    def __init__(self, sheet: str, cell: str) -> None:
        XDispatch.__init__(self)
        LogMixin.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self.add_event_observers(SharedEvent().event_observer)
        self.log.debug("init: sheet=%s, cell=%s", sheet, cell)
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self.log.indent(True):
            self.log.debug("addStatusListener(): url=%s", URL.Main)
            if URL.Complete in self._status_listeners:
                self.log.debug("addStatusListener(): url=%s already exists.", URL.Main)
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=URL, IsEnabled=True, State=None)
                Control.statusChanged(fe)
                self._status_listeners[URL.Complete] = Control

    @override
    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        with self.log.indent(True):
            try:
                self.log.debug("dispatch(): url=%s", URL.Main)
                doc = CalcDoc.from_current_doc()
                sheet = doc.sheets[self._sheet]
                cell = sheet[self._cell]
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(
                    url=URL,
                    args=Arguments,
                    doc=doc,
                    sheet=sheet,
                    cell=cell,
                )
                self.trigger_event(f"{URL.Main}_before_dispatch", cargs)
                if cargs.cancel:
                    self.log.debug("Event %s_before_dispatch was cancelled.", URL.Main)
                    return

                card = TblDataCard2(cell)
                card.show()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = True
                self.trigger_event(f"{URL.Main}_after_dispatch", eargs)
            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self.log.error("Error: %s", e, exc_info=True)
                return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        with self.log.indent(True):
            self.log.debug("removeStatusListener(): url=%s", URL.Main)
            if URL.Complete in self._status_listeners:
                del self._status_listeners[URL.Complete]
