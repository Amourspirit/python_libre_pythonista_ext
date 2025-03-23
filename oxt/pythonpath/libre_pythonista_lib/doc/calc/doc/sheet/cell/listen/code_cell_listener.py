from __future__ import annotations
from typing import Any, cast, Callable, TYPE_CHECKING

import unohelper
from com.sun.star.util import XModifyListener
from ooodev.calc import CalcDoc, CalcCell
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.events.partial.events_partial import EventsPartial
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
# from ..cell_info import CellInfo
# from ...code.cell_cache import CellCache


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import SheetCell  # service
    from oxt.___lo_pip___.basic_config import BasicConfig as Config
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )
    from oxt.pythonpath.libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_doc import QryCellSheetDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import (
        QryCellIsPycFormula,
    )
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_name import QryCellSheetName
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from ___lo_pip___.basic_config import BasicConfig as Config
    from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_doc import QryCellSheetDoc
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_is_deleted import QryCellIsDeleted
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.formula.qry_cell_is_pyc_formula import QryCellIsPycFormula
    from libre_pythonista_lib.cq.qry.calc.sheet.uno_cell.qry_cell_sheet_name import QryCellSheetName
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.mixin.listener.trigger_state_mixin import TriggerStateMixin


class CodeCellListener(XModifyListener, LogMixin, TriggerStateMixin, EventsPartial, unohelper.Base):
    """
    Code Cell Listener

    .. versionadded:: 0.10.0
    """

    def __init__(self, absolute_name: str, code_name: str, cell_obj: CellObj, listeners: CodeCellListeners) -> None:
        """
        Constructor

        Args:
            absolute_name (str): Absolute name of the cell.
            code_name (str): Code name of the cell.
            cell_obj (CellObj): Cell object.
            listeners (CodeCellListeners): Code cell listeners.
        """
        XModifyListener.__init__(self)
        LogMixin.__init__(self)
        TriggerStateMixin.__init__(self)
        EventsPartial.__init__(self)
        unohelper.Base.__init__(self)
        self.log.debug("Init")
        self._absolute_name = absolute_name
        self.code_name = code_name
        self.cell_obj = cell_obj
        self._qry_handler = QryHandler()

    def _get_sheet_name(self, cell: SheetCell) -> str:
        try:
            query = QryCellSheetName(cell=cell)
            return self._qry_handler.handle(query)
        except Exception:
            self.log.error("_get_sheet_name() error.", exc_info=True)
            raise

    @override
    def modified(self, aEvent: EventObject) -> None:  # noqa: N803
        try:
            if not self.is_trigger():
                self.log.debug("modified() Trigger events is False. Returning.")
                return

            qry_cell_deleted = QryCellIsDeleted(cell=aEvent.Source)  # type: ignore
            is_cell_deleted = self._qry_handler.handle(qry_cell_deleted)

            if is_cell_deleted:
                self.log.debug("modified: Cell is deleted")
                # cell is deleted
                calc_cell = self._get_calc_cell(cell=aEvent.Source)  # type: ignore
                eargs = EventArgs(self)

                dd = DotDict(
                    absolute_name=self._absolute_name,
                    event_obj=aEvent,
                    code_name=self.code_name,
                    calc_cell=calc_cell,
                    deleted=True,
                )
                eargs.event_data = dd
                for key, value in dd.items():
                    calc_cell.extra_data[key] = value
                self.trigger_event("cell_deleted", eargs)
                # self.log.debug("modified: Cell is deleted")
                return
            name = aEvent.Source.AbsoluteName  # type: ignore

            qry_cell_pyc_formula = QryCellIsPycFormula(cell=aEvent.Source)  # type: ignore
            is_pyc_formula = self._qry_handler.handle(qry_cell_pyc_formula)

            if not is_pyc_formula:
                calc_cell = self._get_calc_cell(cell=aEvent.Source)  # type: ignore

                eargs = EventArgs(self)
                dd = DotDict(
                    absolute_name=name, event_obj=aEvent, code_name=self.code_name, calc_cell=calc_cell, deleted=False
                )
                eargs.event_data = dd
                for key, value in dd.items():
                    calc_cell.extra_data[key] = value
                trigger_name = "cell_pyc_formula_removed"
                self.log.debug("modified: Triggering event: %s", trigger_name)
                self.trigger_event(trigger_name, eargs)
                return
            if name == self._absolute_name:
                eargs = EventArgs(self)
                calc_cell = self._get_calc_cell(cell=aEvent.Source)  # type: ignore
                # cc = CellCache(calc_cell.calc_doc)
                dd = DotDict(
                    absolute_name=self._absolute_name,
                    event_obj=aEvent,
                    code_name=self.code_name,
                    calc_cell=calc_cell,
                    deleted=False,
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

                        self.log.debug("modified: Triggering event: %s", trigger_name)
                        self.trigger_event("cell_custom_prop_modify", eargs)
                        if eargs.event_data.remove_custom_property and calc_cell.has_custom_property(key):
                            calc_cell.remove_custom_property(key)
                    else:
                        self.trigger_event("cell_modified", eargs)
                except Exception as e:
                    self.log.error(f"modified: {e}", exc_info=True)
                    return

                # self.log.debug("CodeCellListener: modified: Cell is the same")
            else:
                eargs = EventArgs(self)
                calc_cell = self._get_calc_cell(cell=aEvent.Source)  # type: ignore
                eargs.event_data = DotDict(
                    absolute_name=self._absolute_name,
                    old_name=self._absolute_name,
                    event_obj=aEvent,
                    code_name=self.code_name,
                    deleted=False,
                    calc_cell=calc_cell,
                    # cell_info=ci,
                )
                self.trigger_event("cell_moved", eargs)
                self._absolute_name = name
        except Exception:
            self.log.exception("modified() error.")
            raise

    @override
    def disposing(self, Source: EventObject) -> None:  # noqa: N803
        eargs = EventArgs(self)
        eargs.event_data = DotDict(absolute_name=self._absolute_name, event_obj=Source, code_name=self.code_name)
        self.trigger_event("cell_disposing", eargs)
        self.log.debug("disposing")
        self._absolute_name = ""
        self.code_name = ""
        self.log.debug("disposing: Done")

    def _get_calc_cell(self, cell: SheetCell) -> CalcCell:
        # note if the cell is deleted then then CalcCell object will not be the deleted cell.
        # Use the CalcCell.extra_data to set a flag and use that to determine if the cell is deleted.
        try:
            cc = CalcCell.from_obj(cell)
            if cc is not None:
                return cc
        except Exception as e:
            self.log.warning("_get_calc_cell() warning error. %s", e)
        try:
            qry_cell_doc = QryCellSheetDoc(cell=cell)
            doc = cast(CalcDoc, self._qry_handler.handle(qry_cell_doc))
            if doc is None:
                self.log.error("_get_calc_cell() error. Could not get CalcDoc from cell: %s", cell.AbsoluteName)
                raise ValueError("Could not get CalcDoc from cell")

            sheet = doc.sheets[self._get_sheet_name(cell)]
            cell_addr = cell.getCellAddress()
            cell_obj = CellObj.from_idx(col_idx=cell_addr.Column, row_idx=cell_addr.Row, sheet_idx=cell_addr.Sheet)
            return CalcCell(owner=sheet, cell=cell_obj, lo_inst=sheet.lo_inst)
        except Exception:
            self.log.error("_get_calc_cell() error.", exc_info=True)
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
        old_name = self._absolute_name
        old_co = self.cell_obj
        is_db = self.log.is_debug
        self._absolute_name = name
        self.cell_obj = cell_obj
        if is_db:
            self.log.debug("update_absolute_name: Old Name: %s New Name: %s", old_name, name)
            self.log.debug("update_absolute_name: Old Cell Obj: %s New Cell Obj: %s", old_co, self.cell_obj)
            self.log.debug("update_absolute_name: Done")

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
