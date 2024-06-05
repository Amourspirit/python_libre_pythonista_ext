from __future__ import annotations
from typing import TYPE_CHECKING
import os
import sys
import uno
import unohelper
from com.sun.star.task import XJobExecutor
from ooodev.calc import CalcDoc
from ooodev.exceptions.ex import CellError
from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
from ooo.dyn.awt.message_box_type import MessageBoxType
from ooodev.dialog.msgbox import MsgBox


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from pythonpath.libre_pythonista_lib.res.res_resolver import ResResolver
else:
    from libre_pythonista_lib.res.res_resolver import ResResolver

implementation_name = "___lo_identifier___.impl"


class PythonImpl(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._res = ResResolver(self.ctx)

    def trigger(self, event: str):
        print("PythonImpl: trigger: event", event)
        if event == "testing":
            self._do_testing()
        else:
            self._do_pyc_formula()

    def _do_pyc_formula(self):
        try:

            msg = self._res.resolve_string("title10")
            self._logger.debug(msg)
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            try:
                cell = sheet.get_selected_cell()
            except CellError:
                self._logger.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
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
            cell.component.setFormula(
                '=COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.PYIMPL.PYC(SHEET();CELL("ADDRESS"))'
            )
            _ = cell.value
        except Exception as e:
            self._logger.error(f"{self.__class__.__name__} - Error: {e}")

    def _do_testing(self):
        try:

            msg = self._res.resolve_string("title10")
            self._logger.debug(msg)
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            try:
                cell = sheet.get_selected_cell()
            except CellError:
                self._logger.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            if cell.value is not None:
                msg_result = MsgBox.msgbox(
                    msg=self._res.resolve_string("mbmsg002"),
                    title=self._res.resolve_string("mbtitle002"),
                    boxtype=MessageBoxType.QUERYBOX,
                    buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
                )
                if msg_result != MessageBoxResultsEnum.YES:
                    return
            cell.component.setFormula(
                '=COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.TESTINGIMPL.TESTING(1;"$A1$1")'
            )
            _ = cell.value
        except Exception as e:
            self._logger.error(f"{self.__class__.__name__} - Error: {e}")


g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(PythonImpl, implementation_name, ("com.sun.star.task.Job",))
