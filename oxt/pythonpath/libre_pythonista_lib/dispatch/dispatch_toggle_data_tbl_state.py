from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.calc import CalcDoc, CalcCell
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind
from ..event.shared_event import SharedEvent
from ..cell.array.array_tbl import ArrayTbl

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    import pandas as pd
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchToggleDataTblState(XDispatch, EventsPartial, unohelper.Base):
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

        It is only allowed to register URLs for which this XDispatch was explicitly queried.
        Additional arguments (``#...`` or ``?...``) will be ignored.

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
                arr_helper = ArrayTbl(cell)
                arr_helper.add_event_observers(self.event_observer)
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
                cc = CellCache(doc)  # singleton
                # cm = CellMgr(doc)  # singleton
                cell_obj = cell.cell_obj
                sheet_idx = sheet.sheet_index
                if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
                    self._log.error(f"Cell {self._cell} is not in the cache.")
                    eargs = EventArgs.from_args(cargs)
                    eargs.event_data.success = False
                    self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                    return

                # changing the formula should trigger the recalculation.
                # Toggle the formula from a cell formula to a array formula and vice versa.
                formula = cell.component.getFormula()
                if not formula:
                    self._log.error(f"Cell {self._cell} has no formula.")
                    eargs = EventArgs.from_args(cargs)
                    eargs.event_data.success = False
                    self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                    return

                ctl_state = CtlState(cell=cell)
                state = ctl_state.get_state()
                orig_state = state
                if state == StateKind.PY_OBJ:
                    self._log.debug("Current State to DataFrame")
                    state = StateKind.ARRAY
                else:
                    self._log.debug("Current State to Array")
                    state = StateKind.PY_OBJ
                ctl_state.set_state(value=state)

                if state == StateKind.ARRAY:
                    self._log.debug("Changing State to Array")
                    # change the formula to an array formula
                    # The formula must be removed from the cell.
                    # The number of rows and cols must be gotten from the data.
                    # A range must be constructed from the number of rows and cols.
                    # The formula must be set as an array formula on the range.

                    try:
                        self._set_array_formula(cell=cell, dd_args=cargs.event_data, arr_helper=arr_helper)
                    except Exception:
                        ctl_state.set_state(value=orig_state)
                        raise
                elif state == StateKind.PY_OBJ:

                    try:
                        self._log.debug("Changing State to Data Table")
                        self._set_formula(cell=cell, dd_args=cargs.event_data, arr_helper=arr_helper)
                    except Exception:
                        ctl_state.set_state(value=orig_state)
                        raise
                else:
                    self._log.warning(f"Invalid State: {state}")
                    eargs = EventArgs.from_args(cargs)
                    eargs.event_data.success = False
                    self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                    return

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.success = True
                self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                return

            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    def _set_array_formula(self, cell: CalcCell, dd_args: DotDict, arr_helper: ArrayTbl) -> None:
        with self._log.indent(True):
            arr_helper.set_formula_array(**dd_args)

            cm = CellMgr(cell.calc_doc)  # singleton
            cm.update_control(cell)

    def _set_formula(self, cell: CalcCell, dd_args: DotDict, arr_helper: ArrayTbl) -> None:
        with self._log.indent(True):
            arr_helper.set_formula(**dd_args)

            cm = CellMgr(cell.calc_doc)  # singleton
            cm.update_control(cell)

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        with self._log.indent(True):
            self._log.debug(f"removeStatusListener(): url={url.Main}")
            if url.Complete in self._status_listeners:
                del self._status_listeners[url.Complete]
