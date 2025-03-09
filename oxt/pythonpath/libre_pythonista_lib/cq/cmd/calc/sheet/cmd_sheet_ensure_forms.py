from __future__ import annotations
from typing import cast, TYPE_CHECKING, Any

from ooodev.utils.gen_util import NULL_OBJ


if TYPE_CHECKING:
    from ooodev.calc import CalcSheet, CalcForm
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.draw_page.form.qry_lp_form import QryLpForm
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override

else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cmd_sheet_t import CmdSheetT
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName
    from libre_pythonista_lib.cq.qry.calc.sheet.draw_page.form.qry_lp_form import QryLpForm
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.custom_ext import override

    CalcForm = Any

# tested in: tests/test_cmd/test_cmd_sheet_ensure_forms.py


class CmdSheetEnsureForms(CmdBase, LogMixin, CmdSheetT):
    """Add OnCalculate event to sheet"""

    def __init__(self, sheet: CalcSheet) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.SHEET
        self._sheet = sheet
        self._has_calc_event = cast(bool, NULL_OBJ)
        self._current_form = cast(CalcForm | None, NULL_OBJ)
        self._added_form1 = False
        self._added_form_lp = False

    def _get_current_form(self) -> CalcForm | None:
        qry = QryLpForm(sheet=self._sheet)
        return self._execute_qry(qry)

    def _get_form_name(self) -> str:
        qry = QryFormName()
        return self._execute_qry(qry)

    @override
    def execute(self) -> None:
        """
        Executes the command to ensure forms exist on the sheet.

        If the forms already exist, the method returns immediately; Otherwise, it adds the necessary forms.
        """
        self.success = False
        self._added_form1 = False
        self._added_form_lp = False
        if self._current_form is NULL_OBJ:
            self._current_form = self._get_current_form()

        if self._current_form is not None:
            self.success = True
            self.log.debug("Form already exists. Nothing to do.")
            self.log.debug("Successfully executed command.")
            return

        try:
            form_name = self._get_form_name()
            if len(self._sheet.draw_page.forms) == 0:
                # insert a default user form so custom controls can be on a separate form
                self._sheet.draw_page.forms.add_form("Form1")
                self._added_form1 = True
            if not self._sheet.draw_page.forms.has_by_name(form_name):
                self._sheet.draw_page.forms.add_form(form_name)
                self._added_form_lp = True
        except Exception:
            self.log.exception("Error executing command")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        try:
            form_name = self._get_form_name()
            if self._added_form1 and self._sheet.draw_page.forms.has_by_name("Form1"):
                self._sheet.draw_page.forms.remove_by_name("Form1")
            if self._added_form_lp and self._sheet.draw_page.forms.has_by_name(form_name):
                self._sheet.draw_page.forms.remove_by_name(form_name)
            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing command")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
