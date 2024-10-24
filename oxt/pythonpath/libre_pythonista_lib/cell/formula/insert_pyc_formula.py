from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib

from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
from ooo.dyn.awt.message_box_type import MessageBoxType

from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ooodev.exceptions.ex import CellError
from ooodev.dialog.msgbox import MsgBox
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from .....pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    from .....pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from .....pythonpath.libre_pythonista_lib.const.event_const import PYC_FORMULA_INSERTING, PYC_FORMULA_INSERTED
    from .....pythonpath.libre_pythonista_lib.code.cell_cache import CellCache

else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.const import FORMULA_PYC
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import PYC_FORMULA_INSERTING, PYC_FORMULA_INSERTED
    from libre_pythonista_lib.code.cell_cache import CellCache


class InsertPycFormula:
    def __init__(
        self,
    ) -> None:
        self.ctx = Lo.get_context()
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._res = ResourceResolver(self.ctx)
        self._se = SharedEvent()
        self._doc = CalcDoc.from_current_doc()
        self._sheet = self._doc.get_active_sheet()
        self._sheet_locked = self._sheet.is_sheet_protected()

    def pyc_formula(self):
        global FORMULA_PYC
        try:

            msg = self._res.resolve_string("title10")
            self._log.debug(msg)
            try:
                cell = self._sheet.get_selected_cell()
            except CellError:
                self._log.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            cell_locked = cell.cell_protection.is_locked
            if cell_locked and self._sheet_locked:
                MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg003"),
                    title=self._res.resolve_string("mbtitle003"),
                    boxtype=MessageBoxType.INFOBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_OK,
                )
                return
            if cell.value is not None:
                msg_result = MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg002"),
                    title=self._res.resolve_string("mbtitle002"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if msg_result != MessageBoxResultsEnum.YES:
                    return
            # cell.component.setFormula("=" + res.resolve_string("fml001"))
            formula = f'={FORMULA_PYC}(SHEET();CELL("ADDRESS"))'
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(formula=formula, is_dependent=False, sheet=self._sheet, cell=cell)
            self._se.trigger_event(PYC_FORMULA_INSERTING, cargs)
            if cargs.cancel and not cargs.handled:
                self._log.debug(f"Event {PYC_FORMULA_INSERTING} was cancelled")
                return
            cell.component.setFormula(formula.upper())
            _ = cell.value
            eargs = EventArgs.from_args(cargs)
            self._se.trigger_event(PYC_FORMULA_INSERTED, eargs)
        except Exception as e:
            self._log.error(f"{self.__class__.__name__} - Error: {e}")

    def formula_with_dependent(self):
        global FORMULA_PYC
        try:

            msg = self._res.resolve_string("title10")
            self._log.debug(msg)

            try:
                cell = self._sheet.get_selected_cell()
            except CellError:
                self._log.error(f"{self.__class__.__name__} - No cell selected")
                return
            if self._log.is_debug:
                self._log.debug(f"Selected cell: {cell.cell_obj} with sheet index of {cell.cell_obj.sheet_idx}")
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            cell_locked = cell.cell_protection.is_locked
            if cell_locked and self._sheet_locked:
                MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg003"),
                    title=self._res.resolve_string("mbtitle003"),
                    boxtype=MessageBoxType.INFOBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_OK,
                )
                return
            if cell.value is not None:
                msg_result = MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg002"),
                    title=self._res.resolve_string("mbtitle002"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if msg_result != MessageBoxResultsEnum.YES:
                    return

            cc = CellCache(self._doc)

            formula = f'={FORMULA_PYC}(SHEET();CELL("ADDRESS")'
            with cc.set_context(cell=cell.cell_obj, sheet_idx=self._sheet.sheet_index):
                found = cc.get_cell_before()
                if found:
                    formula += ";"
                    if found.sheet_idx > -1 and found.sheet_idx != cc.current_sheet_index:
                        with contextlib.suppress(Exception):
                            # maybe the sheet has been deleted
                            prev_sheet = self._doc.get_sheet(cc.previous_sheet_index)
                            formula += f"${prev_sheet.name}."

                    formula += f"{found.col.upper()}{found.row}"
                formula += ")"

            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(formula=formula, is_dependent=True, sheet=self._sheet, cell=cell)
            self._se.trigger_event(PYC_FORMULA_INSERTING, cargs)
            if cargs.cancel and not cargs.handled:
                self._log.debug(f"Event {PYC_FORMULA_INSERTING} was cancelled")
                return
            # cell.component.setFormula("=" + res.resolve_string("fml001"))
            cell.component.setFormula(formula)
            _ = cell.value
            eargs = EventArgs.from_args(cargs)
            self._se.trigger_event(PYC_FORMULA_INSERTED, eargs)
        except Exception as e:
            self._log.error(f"{self.__class__.__name__} - Error: {e}")
