from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING
import uno
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

from ..dialog.card.tbl_data_card import TblDataCard
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchCardTblData(XDispatch, EventsPartial, unohelper.Base):
    def __init__(self, sheet: str, cell: str):
        XDispatch.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self.add_event_observers(SharedEvent().event_observer)
        self._log.debug(f"init: sheet={sheet}, cell={cell}")
        self._status_listeners: Dict[str, XStatusListener] = {}

    def addStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        with self._log.indent(True):
            self._log.debug(f"addStatusListener(): url={url.Main}")
            if url.Complete in self._status_listeners:
                self._log.debug(f"addStatusListener(): url={url.Main} already exists.")
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=url, IsEnabled=True, State=None)
                control.statusChanged(fe)
                self._status_listeners[url.Complete] = control

    def dispatch(self, url: URL, args: Tuple[PropertyValue, ...]) -> None:
        """
        Dispatches (executes) a URL

        It is only allowed to dispatch URLs for which this XDispatch was explicitly queried. Additional arguments (``#...`` or ``?...``) are allowed.

        Controlling synchronous or asynchronous mode happens via readonly boolean Flag SynchronMode.

        By default, and absent any arguments, ``SynchronMode`` is considered ``False`` and the execution is performed asynchronously (i.e. dispatch() returns immediately, and the action is performed in the background).
        But when set to ``True``, dispatch() processes the request synchronously.
        """
        with self._log.indent(True):
            try:
                self._log.debug(f"dispatch(): url={url.Main}")
                doc = CalcDoc.from_current_doc()
                sheet = doc.sheets[self._sheet]
                cell = sheet[self._cell]
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(
                    url=url,
                    args=args,
                    doc=doc,
                    sheet=sheet,
                    cell=cell,
                )
                self.trigger_event(f"{url.Main}_before_dispatch", cargs)
                if cargs.cancel:
                    self._log.debug(f"Event {url.Main}_before_dispatch was cancelled.")
                    return

                card = TblDataCard(cell)
                card.show()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = True
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        with self._log.indent(True):
            self._log.debug(f"removeStatusListener(): url={url.Main}")
            if url.Complete in self._status_listeners:
                del self._status_listeners[url.Complete]
