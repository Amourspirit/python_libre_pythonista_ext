from __future__ import annotations
from typing import TYPE_CHECKING, Union

from ooodev.calc import CalcForm

if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.cq.qry.calc.common.qry_form_name import QryFormName

# tested in: tests/test_cmd/test_cmd_sheet_ensure_forms.py


class QryLpForm(QryBase, LogMixin, QrySheetT[Union[CalcForm, None]]):
    def __init__(self, sheet: CalcSheet) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET
        self._sheet = sheet
        self.log.debug("init done for sheet %s", sheet.name)

    def _get_form_name(self) -> str:
        qry = QryFormName()
        return self._execute_qry(qry)

    def execute(self) -> Union[CalcForm, None]:
        """
        Executes the query to get the form.

        Returns:
            CalcForm, None: The form if successful, otherwise None.
        """

        try:
            if len(self._sheet.draw_page.forms) == 0:
                self.log.debug("No forms found")
                return None
            name = self._get_form_name()
            if not self._sheet.draw_page.forms.has_by_name(name):
                self.log.debug("Form not found: %s", name)
                return None
            return self._sheet.draw_page.forms.get_by_name(name)
        except Exception:
            self.log.exception("Error getting form")
        return None

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
