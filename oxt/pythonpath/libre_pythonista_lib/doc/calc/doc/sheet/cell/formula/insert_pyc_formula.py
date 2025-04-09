from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib

from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
from ooo.dyn.awt.message_box_type import MessageBoxType

from ooodev.loader import Lo
from ooodev.calc import CalcDoc, CalcCell
from ooodev.exceptions.ex import CellError
from ooodev.dialog.msgbox import MsgBox
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const import FORMULA_PYC
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import PYC_FORMULA_INSERTING, PYC_FORMULA_INSERTED
    from oxt.pythonpath.libre_pythonista_lib.code.cell_cache import CellCache
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_is_lp_cell import QryIsLpCell
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_lp_cell import CmdDeleteLpCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_prev import QryCellPrev
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import (
        CodeCellListeners,
    )

else:
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.const import FORMULA_PYC
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import PYC_FORMULA_INSERTING, PYC_FORMULA_INSERTED
    from libre_pythonista_lib.code.cell_cache import CellCache
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_is_lp_cell import QryIsLpCell
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.state.cmd_delete_lp_cell import CmdDeleteLpCell
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_prev import QryCellPrev
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.listen.code_cell_listeners import CodeCellListeners


class InsertPycFormula(LogMixin):
    def __init__(
        self,
    ) -> None:
        self.ctx = Lo.get_context()
        LogMixin.__init__(self)
        self._res = ResourceResolver(self.ctx)
        self._se = SharedEvent()
        self._doc = CalcDoc.from_current_doc()
        self._sheet = self._doc.get_active_sheet()
        self._sheet_locked = self._sheet.is_sheet_protected()

    def _cleanup_lp_cell(self, cell: CalcCell) -> None:
        self.log.debug("_cleanup_lp_cell() Cleaning up LibrePythonista cell: %s", cell.cell_obj)
        cmd_handler = CmdHandlerFactory.get_cmd_handler()
        qry_handler = QryHandlerFactory.get_qry_handler()
        qry = QryIsLpCell(cell=cell)
        is_lp_cell = qry_handler.handle(qry)
        if not is_lp_cell:
            self.log.debug("Cell is not a LibrePythonista cell. Returning.")
            return
        cmd = CmdDeleteLpCell(cell=cell)
        cmd_handler.handle(cmd)
        if cmd.success:
            self.log.debug("Successfully deleted LibrePythonista cell: %s", cell.cell_obj)
        else:
            self.log.error("Failed to delete LibrePythonista cell: %s", cell.cell_obj)

    def pyc_formula(self) -> None:
        global FORMULA_PYC
        try:
            msg = self._res.resolve_string("title10")
            self.log.debug(msg)
            try:
                cell = self._sheet.get_selected_cell()
            except CellError:
                self.log.error("No cell selected")
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
                self._cleanup_lp_cell(cell=cell)
            # cell.component.setFormula("=" + res.resolve_string("fml001"))
            formula = f'={FORMULA_PYC}(SHEET();CELL("ADDRESS"))'
            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(formula=formula, is_dependent=False, sheet=self._sheet, cell=cell)
            self._se.trigger_event(PYC_FORMULA_INSERTING, cargs)
            if cargs.cancel and not cargs.handled:
                self.log.debug("Event %s was cancelled", PYC_FORMULA_INSERTING)
                return
            cell.component.setFormula(formula.upper())
            _ = cell.value
            eargs = EventArgs.from_args(cargs)
            self._se.trigger_event(PYC_FORMULA_INSERTED, eargs)
        except Exception as e:
            self.log.error("Error: %s", e)

    def formula_with_dependent(self) -> None:
        global FORMULA_PYC
        try:
            msg = self._res.resolve_string("title10")
            self.log.debug(msg)

            try:
                cell = self._sheet.get_selected_cell()
            except CellError:
                self.log.error("No cell selected")
                return
            if self.log.is_debug:
                self.log.debug("Selected cell: %s with sheet index of %i", cell.cell_obj, cell.cell_obj.sheet_idx)
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
                self._cleanup_lp_cell(cell=cell)

            formula = f'={FORMULA_PYC}(SHEET();CELL("ADDRESS")'
            qry_cell_prev = QryCellPrev(cell=cell)
            qry_handler = QryHandlerFactory.get_qry_handler()
            qry_result = qry_handler.handle(qry_cell_prev)
            if Result.is_success(qry_result):
                found = qry_result.data
                formula += ";"
                if found.sheet_idx > -1 and found.sheet_idx != self._sheet.sheet_index:
                    with contextlib.suppress(Exception):
                        self.log.debug("Previous cell is on a different sheet")
                        prev_sheet = self._doc.get_sheet(found.sheet_idx)
                        formula += f"${prev_sheet.name}."

                formula += f"{found.col.upper()}{found.row}"
            else:
                self.log.debug("no previous cell: %s", qry_result.error)
            formula += ")"

            cargs = CancelEventArgs(self)
            cargs.event_data = DotDict(formula=formula, is_dependent=True, sheet=self._sheet, cell=cell)
            self._se.trigger_event(PYC_FORMULA_INSERTING, cargs)
            if cargs.cancel and not cargs.handled:
                self.log.debug("Event %s was cancelled", PYC_FORMULA_INSERTING)
                return
            cell.component.setFormula(formula)
            _ = cell.value
            eargs = EventArgs.from_args(cargs)
            self._se.trigger_event(PYC_FORMULA_INSERTED, eargs)
        except Exception as e:
            self.log.error("Error: %s", e)
