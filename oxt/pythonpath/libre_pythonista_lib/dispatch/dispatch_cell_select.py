from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent

from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.utils.data_type.range_values import RangeValues

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchCellSelect(unohelper.Base, XDispatch):
    """If the View is not in PY_OBJ state the it is switched into PY_OBJ State."""

    def __init__(self, sheet: str, cell: str):
        super().__init__()
        self._sheet = sheet
        self._cell = cell
        self._log = OxtLogger(log_name=self.__class__.__name__)
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
            if url.Complete in self._status_listeners:
                self._log.debug(f"addStatusListener(): url={url.Main} already exists.")
            else:
                # setting IsEnable=False here does not disable the dispatch command
                # State=True may cause the menu items to be displayed as checked.
                fe = FeatureStateEvent(FeatureURL=url, IsEnabled=True, State=None)
                control.statusChanged(fe)
                self._status_listeners[url.Complete] = control

    def _get_range_obj(self, cell: CalcCell) -> RangeValues:
        if cell.component.IsMerged:  # type: ignore
            cursor = cell.calc_sheet.create_cursor_by_range(cell_obj=cell.cell_obj)
            cursor.component.collapseToMergedArea()
            rng = cursor.get_calc_cell_range()
            rv = rng.range_obj.get_range_values()

        else:
            cv = cell.cell_obj.get_cell_values()
            rv = RangeValues(col_start=cv.col, row_start=cv.row, col_end=cv.col, row_end=cv.row)
        return rv

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
                rv = self._get_range_obj(cell)
                sheet.select_cells_range(RangeObj.from_range(rv))

                return

            except Exception as e:
                # log the error and do not re-raise it.
                # re-raising the error may crash the entire LibreOffice app.
                self._log.error(f"Error: {e}", exc_info=True)
                return

    def removeStatusListener(self, control: XStatusListener, url: URL) -> None:
        """
        Un-registers a listener from a control.
        """
        if url.Complete in self._status_listeners:
            del self._status_listeners[url.Complete]
