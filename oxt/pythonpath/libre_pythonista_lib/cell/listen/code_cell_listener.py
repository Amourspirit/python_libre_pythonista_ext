from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING
import uno
import unohelper
from com.sun.star.util import XModifyListener
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ..cell_info import CellInfo


if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import SheetCell
    from .....___lo_pip___.config import Config
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .code_cell_listeners import CodeCellListeners
else:
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

# This listener is used by CellMgr.
# When source code is added to CellMgr is will add this listener to the cell.


class CodeCellListener(unohelper.Base, XModifyListener, EventsPartial):

    def __init__(self, absolute_name: str, code_name: str, cell_obj: CellObj, listeners: CodeCellListeners) -> None:
        XModifyListener.__init__(self)
        EventsPartial.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("Init")
        self._absolute_name = absolute_name
        self.code_name = code_name
        self.cell_obj = cell_obj
        self.listeners = listeners
        # self._log.debug(f"CodeCellListener: init Absolute Name: {absolute_name}")

    def _get_sheet_name(self, cell: Any) -> str:
        try:

            rng = cell.getSpreadsheet()  # com.sun.star.sheet.XSpreadsheet
            sheet_name = rng.getName()
            return sheet_name
        except Exception:
            self._log.error("_get_sheet_name() error.", exc_info=True)
            raise

    def modified(self, event: EventObject) -> None:
        with self._log.indent(True):
            ci = CellInfo(cell=event.Source)  # type: ignore
            if ci.is_cell_deleted():
                self._log.debug("modified: Cell is deleted")
                # cell is deleted
                calc_cell = self._get_calc_cell(cell=event.Source)  # type: ignore
                eargs = EventArgs(self)

                dd = DotDict(
                    absolute_name=self._absolute_name,
                    event_obj=event,
                    code_name=self.code_name,
                    calc_cell=calc_cell,
                    deleted=True,
                    cell_info=ci,
                )
                eargs.event_data = dd
                for key, value in dd.items():
                    calc_cell.extra_data[key] = value
                self.trigger_event("cell_deleted", eargs)
                # self._log.debug("modified: Cell is deleted")
                return
            name = event.Source.AbsoluteName  # type: ignore
            if not ci.is_pyc_formula():
                calc_cell = self._get_calc_cell(cell=event.Source)  # type: ignore

                eargs = EventArgs(self)
                dd = DotDict(
                    absolute_name=name, event_obj=event, code_name=self.code_name, calc_cell=calc_cell, deleted=False
                )
                eargs.event_data = dd
                for key, value in dd.items():
                    calc_cell.extra_data[key] = value
                trigger_name = "cell_pyc_formula_removed"
                self._log.debug(f"modified: Triggering event: {trigger_name}")
                self.trigger_event(trigger_name, eargs)
                return
            if name == self._absolute_name:
                eargs = EventArgs(self)
                calc_cell = self._get_calc_cell(cell=event.Source)  # type: ignore
                dd = DotDict(
                    absolute_name=self._absolute_name,
                    event_obj=event,
                    code_name=self.code_name,
                    calc_cell=calc_cell,
                    deleted=False,
                    cell_info=ci,
                )
                eargs.event_data = dd
                try:
                    for key, value in dd.items():
                        calc_cell.extra_data[key] = value
                    # doc = CalcDoc.from_current_doc()
                    # sheet = doc.sheets[self._get_sheet_name(event.Source)]
                    # cell = cast("SheetCell", event.Source)
                    # cell_addr = cell.getCellAddress()
                    # cell_obj = CellObj.from_idx(col_idx=cell_addr.Column, row_idx=cell_addr.Row, sheet_idx=cell_addr.Sheet)
                    # calc_cell = CalcCell(owner=sheet, cell=cell_obj, lo_inst=sheet.lo_inst)
                    cfg = Config()
                    key = f"{cfg.cell_cp_prefix}modify_trigger_event"
                    if calc_cell.has_custom_property(key):
                        trigger_name = str(calc_cell.get_custom_property(key))
                        eargs.event_data.trigger_name = trigger_name
                        eargs.event_data.remove_custom_property = False
                        eargs.event_data.calc_cell = calc_cell
                        eargs.event_data.cell_cp_codename = cfg.cell_cp_codename

                        self._log.debug(f"modified: Triggering event: {trigger_name}")
                        self.trigger_event("cell_custom_prop_modify", eargs)
                        if eargs.event_data.remove_custom_property:
                            if calc_cell.has_custom_property(key):
                                calc_cell.remove_custom_property(key)
                    else:
                        self.trigger_event("cell_modified", eargs)
                except Exception as e:
                    self._log.error(f"modified: {e}", exc_info=True)
                    return

                # self._log.debug("CodeCellListener: modified: Cell is the same")
            else:
                eargs = EventArgs(self)
                calc_cell = self._get_calc_cell(cell=event.Source)  # type: ignore
                eargs.event_data = DotDict(
                    absolute_name=self._absolute_name,
                    old_name=self._absolute_name,
                    event_obj=event,
                    code_name=self.code_name,
                    deleted=False,
                    calc_cell=calc_cell,
                    cell_info=ci,
                )
                self.trigger_event("cell_moved", eargs)
                self._absolute_name = name

    def disposing(self, event: EventObject) -> None:
        with self._log.indent(True):
            eargs = EventArgs(self)
            eargs.event_data = DotDict(absolute_name=self._absolute_name, event_obj=event, code_name=self.code_name)
            self.trigger_event("cell_disposing", eargs)
            self._log.debug("disposing")
            self._absolute_name = ""
            self.code_name = ""
            self._log.debug("disposing: Done")

    def _get_calc_cell(self, cell: SheetCell) -> CalcCell:
        # note if the cell is deleted then then CalcCell object will not be the deleted cell.
        # Use the CalcCell.extra_data to set a flag and use that to determine if the cell is deleted.
        with self._log.indent(True):
            try:
                cc = CalcCell.from_obj(cell)
                if cc is not None:
                    return cc
            except Exception as e:
                self._log.warning(
                    f"_get_calc_cell() warning error. {e}",
                )
            try:
                doc = CalcDoc.from_current_doc()
                sheet = doc.sheets[self._get_sheet_name(cell)]
                cell_addr = cell.getCellAddress()
                cell_obj = CellObj.from_idx(col_idx=cell_addr.Column, row_idx=cell_addr.Row, sheet_idx=cell_addr.Sheet)
                return CalcCell(owner=sheet, cell=cell_obj, lo_inst=sheet.lo_inst)
            except Exception:
                self._log.error("_get_calc_cell() error.", exc_info=True)
                raise

    def update_absolute_name(self, name: str, cell_obj: CellObj) -> None:
        """
        Updates the Absolute Name of the cell.

        Args:
            name (str): The new Absolute Name of the cell.
            cell_obj (CellObj): The new Cell Object.

        Note:
            When a cell has been moved the Absolute Name will be updated.
            When the current instance was created it captured the Absolute Name of the cell.
            Other event may occur that refresh the cell's Position such as
            the ``CellCache.update_sheet_cell_addr_prop()`` and the ``CellMgr.update_cell_addr_prop()``.
        """
        with self._log.indent(True):
            old_name = self._absolute_name
            old_co = self.cell_obj
            is_db = self._log.is_debug
            self._absolute_name = name
            self.cell_obj = cell_obj
            if is_db:
                self._log.debug(f"update_absolute_name: Old Name: {old_name} New Name: {name}")
                self._log.debug(f"update_absolute_name: Old Cell Obj: {old_co} New Cell Obj: {self.cell_obj}")
                self._log.debug("update_absolute_name: Done")

    def subscribe_cell_deleted(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_deleted", cb)

    def subscribe_cell_modified(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_modified", cb)

    def subscribe_cell_custom_prop_modify(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_custom_prop_modify", cb)

    def subscribe_cell_moved(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_moved", cb)

    def subscribe_cell_pyc_formula_removed(self, cb: Callable[[Any, Any], None]) -> None:
        self.subscribe_event("cell_pyc_formula_removed", cb)

    def unsubscribe_cell_deleted(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_deleted", cb)

    def unsubscribe_cell_modified(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_modified", cb)

    def unsubscribe_cell_moved(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_moved", cb)

    def unsubscribe_cell_custom_prop_modify(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_custom_prop_modify", cb)

    def unsubscribe_cell_pyc_formula_removed(self, cb: Callable[[Any, Any], None]) -> None:
        self.unsubscribe_event("cell_pyc_formula_removed", cb)
