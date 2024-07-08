from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ooodev.utils.data_type.range_obj import RangeObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..dialog.py.dialog_python import DialogPython
from ..code.cell_cache import CellCache
from ..cell.cell_mgr import CellMgr
from ..code.py_source_mgr import PyInstance
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from com.sun.star.sheet import SheetCellCursor
    from ooodev.utils.data_type.cell_obj import CellObj
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class DispatchEditPyCell(XDispatch, EventsPartial, unohelper.Base):
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

                cc = CellCache(doc)  # singleton
                cell_obj = cell.cell_obj
                sheet_idx = sheet.sheet_index
                if not cc.has_cell(cell=cell_obj, sheet_idx=sheet_idx):
                    self._log.error(f"Cell {self._cell} is not in the cache.")
                    return
                with cc.set_context(cell=cell_obj, sheet_idx=sheet_idx):
                    result = self._edit_code(doc=doc, cell_obj=cell_obj)
                    if result:
                        if doc.component.isAutomaticCalculationEnabled():
                            # the purpose of writing the formulas back to the cell(s) is to trigger the recalculation
                            cm = CellMgr(doc)  # singleton. Tracks all Code cells
                            # https://ask.libreoffice.org/t/mark-a-calc-sheet-cell-as-dirty/106659
                            with cm.listener_context(cell.component):
                                # suspend the listeners for this cell
                                formula = cell.component.getFormula()
                                if not formula:
                                    self._log.error(f"Cell {self._cell} has no formula.")
                                    eargs = EventArgs.from_args(cargs)
                                    eargs.event_data.success = False
                                    self.trigger_event(f"{url.Main}_after_dispatch", eargs)
                                    return
                                # s = s.lstrip("=")  # just in case there are multiple equal signs
                                is_formula_array = False
                                if formula.startswith("{"):
                                    is_formula_array = True
                                    formula = formula.lstrip("{")
                                    formula = formula.rstrip("}")

                                dd = DotDict()
                                for key, value in cargs.event_data.items():
                                    dd[key] = value
                                eargs = EventArgs(self)
                                if is_formula_array:
                                    # The try block is important. If there is a error without the block then the entire LibreOffice app can crash.
                                    self._log.debug("Resetting array formula")
                                    # get the cell that are involved in the array formula.
                                    cursor = cast("SheetCellCursor", sheet.component.createCursorByRange(cell.component))  # type: ignore
                                    # this next line also works.
                                    # cursor = cast("SheetCellCursor", cell.component.getSpreadsheet().createCursorByRange(cell.component))  # type: ignore
                                    cursor.collapseToCurrentArray()
                                    # reset the array formula
                                    cursor.setArrayFormula(formula)
                                    rng_addr = cursor.getRangeAddress()
                                    dd.range_obj = RangeObj.from_range(rng_addr)
                                    eargs.event_data = dd
                                    self.trigger_event("dispatch_remove_array_formula", eargs)
                                else:
                                    self._log.debug("Resetting formula")
                                    cell.component.setFormula(formula)
                                    self.trigger_event("dispatch_added_cell_formula", eargs)
                                doc.component.calculate()
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

    def _edit_code(self, doc: CalcDoc, cell_obj: CellObj) -> bool:
        with self._log.indent(True):
            ctx = Lo.get_context()
            dlg = DialogPython(ctx)
            py_inst = PyInstance(doc)  # singleton
            py_src = py_inst[cell_obj]
            code = py_src.source_code
            py_src = None
            self._log.debug("Displaying dialog")
            dlg.text = code
            result = False
            if dlg.show():
                self._log.debug("Dialog returned with OK")
                txt = dlg.text.strip()
                if txt != code:
                    try:
                        self._log.debug("Code has changed, updating ...")
                        py_inst.update_source(code=txt, cell=cell_obj)
                        self._log.debug(f"Cell Code updated for {cell_obj}")
                        py_inst.update_all()
                        self._log.debug("Code updated")
                        result = True
                    except Exception as e:
                        self._log.error("Error updating code", exc_info=True)
                else:
                    self._log.debug("Code has not changed")
            else:
                self._log.debug("Dialog returned with Cancel")
            return result
