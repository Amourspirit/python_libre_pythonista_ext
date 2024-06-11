from __future__ import annotations
from typing import Any, cast, Callable, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.util import XModifyListener
from com.sun.star.uno import RuntimeException
from ooodev.calc import CalcDoc, CalcSheet, CalcCell
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.sheet import XSpreadsheet
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import SheetCell
    from .....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CodeCellListener(unohelper.Base, XModifyListener, EventsPartial):

    def __init__(self, absolute_name: str, code_name: str) -> None:
        XModifyListener.__init__(self)
        EventsPartial.__init__(self)
        self._log = LogInst()
        self._absolute_name = absolute_name
        self._code_name = code_name
        # self._log.debug(f"CodeCellListener: init Absolute Name: {absolute_name}")

    def _get_sheet_name(self, cell: Any) -> str:
        try:

            rng = cell.getSpreadsheet()  # com.sun.star.sheet.XSpreadsheet
            sheet_name = rng.getName()
            return sheet_name
        except Exception:
            self._log.error("CodeCellListener: _get_sheet_name() error.", exc_info=True)
            raise

    def modified(self, event: EventObject) -> None:

        try:
            name = event.Source.AbsoluteName  # type: ignore
            # self._log.debug(f"CodeCellListener: modified: {name}")
        except RuntimeException:
            # cell is deleted
            eargs = EventArgs(self)
            eargs.event_data = DotDict(absolute_name=self._absolute_name, event_obj=event, code_name=self._code_name)
            self.trigger_event("cell_deleted", eargs)
            # self._log.debug("CodeCellListener: modified: Cell is deleted")
            return
        if name == self._absolute_name:
            eargs = EventArgs(self)
            eargs.event_data = DotDict(absolute_name=self._absolute_name, event_obj=event, code_name=self._code_name)
            try:
                doc = CalcDoc.from_current_doc()
                sheet = doc.sheets[self._get_sheet_name(event.Source)]
                cell = cast("SheetCell", event.Source)
                cell_addr = cell.getCellAddress()
                cell_obj = CellObj.from_idx(col_idx=cell_addr.Column, row_idx=cell_addr.Row, sheet_idx=cell_addr.Sheet)
                calc_cell = CalcCell(owner=sheet, cell=cell_obj, lo_inst=sheet.lo_inst)
                cfg = Config()
                key = f"{cfg.cell_cp_prefix}_modify_trigger_event"
                if calc_cell.has_custom_property(key):
                    trigger_name = str(calc_cell.get_custom_property(key))
                    eargs.event_data.trigger_name = trigger_name
                    eargs.event_data.remove_custom_property = True
                    self._log.debug(f"CodeCellListener: modified: Triggering event: {trigger_name}")
                    self.trigger_event(trigger_name, eargs)
                    if eargs.event_data.remove_custom_property:
                        calc_cell.remove_custom_property(key)
                else:
                    self.trigger_event("cell_modified", eargs)
            except Exception as e:
                self._log.error(f"CodeCellListener: modified: {e}", exc_info=True)
                return

            # self._log.debug("CodeCellListener: modified: Cell is the same")
        else:
            eargs = EventArgs(self)
            eargs.event_data = DotDict(
                absolute_name=self._absolute_name,
                old_name=self._absolute_name,
                event_obj=event,
                code_name=self._code_name,
            )
            self.trigger_event("cell_moved", eargs)
            # self._log.debug(
            #     f"CodeCellListener: modified: Cell is different. New Name: '{name}'. Old Name: '{self._absolute_name}'"
            # )
            self._absolute_name = name

    def disposing(self, event: EventObject) -> None:
        eargs = EventArgs(self)
        eargs.event_data = DotDict(absolute_name=self._absolute_name, event_obj=event, code_name=self._code_name)
        self.trigger_event("cell_disposing", eargs)
        self._log.debug("CodeCellListener: disposing")
        self._absolute_name = ""
        self._code_name = ""
        self._log.debug("CodeCellListener: disposing: Done")

    def subscribe_cell_deleted(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_deleted", cb)

    def subscribe_cell_modified(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_modified", cb)

    def subscribe_cell_moved(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_moved", cb)

    def unsubscribe_cell_deleted(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_deleted", cb)

    def unsubscribe_cell_modified(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_modified", cb)

    def unsubscribe_cell_moved(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_moved", cb)
