from __future__ import annotations
from typing import TYPE_CHECKING
import contextlib
import os
import sys
import uno
import unohelper
from com.sun.star.task import XJobExecutor


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from .___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from .pythonpath.libre_pythonista_lib.code.cell_cache import CellCache
    from .pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstance
    from ooodev.calc import CalcDoc
    from ooodev.exceptions.ex import CellError
    from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
    from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
    from ooo.dyn.awt.message_box_type import MessageBoxType
    from ooodev.dialog.msgbox import MsgBox
    from .___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ooodev.exceptions.ex import CellError
        from ooo.dyn.awt.message_box_results import MessageBoxResultsEnum
        from ooo.dyn.awt.message_box_buttons import MessageBoxButtonsEnum
        from ooo.dyn.awt.message_box_type import MessageBoxType
        from ooodev.dialog.msgbox import MsgBox
        from libre_pythonista_lib.code.cell_cache import CellCache
        from libre_pythonista_lib.code.py_source_mgr import PyInstance
    from ___lo_pip___.lo_util.resource_resolver import ResourceResolver
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


implementation_name = "___lo_identifier___.impl"


class PythonImpl(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._res = ResourceResolver(self.ctx)

    def trigger(self, event: str):
        print("PythonImpl: trigger: event", event)
        if not _CONDITIONS_MET:
            return
        if event == "testing":
            self._do_testing()
        elif event == "pyc_formula_with_dependent":
            self._do_pyc_formula_with_dependent()
        elif event == "debug_dump_module_to_log":
            self._debug_dump_module_to_log()
        else:
            self._do_pyc_formula()

    def _do_pyc_formula(self):
        try:

            msg = self._res.resolve_string("title10")
            self._logger.debug(msg)
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            sheet_locked = sheet.is_sheet_protected()
            try:
                cell = sheet.get_selected_cell()
            except CellError:
                self._logger.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            cell_locked = cell.cell_protection.is_locked
            if cell_locked and sheet_locked:
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
            cell.component.setFormula(
                '=COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.PYIMPL.PYC(SHEET();CELL("ADDRESS"))'
            )
            _ = cell.value
        except Exception as e:
            self._logger.error(f"{self.__class__.__name__} - Error: {e}")

    def _do_pyc_formula_with_dependent(self):
        try:

            msg = self._res.resolve_string("title10")
            self._logger.debug(msg)
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            sheet_locked = sheet.is_sheet_protected()
            try:
                cell = sheet.get_selected_cell()
            except CellError:
                self._logger.error(f"{self.__class__.__name__} - No cell selected")
                return
            # https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1awt_1_1MessageBoxButtons.html
            cell_locked = cell.cell_protection.is_locked
            if cell_locked and sheet_locked:
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
            cc = CellCache(doc)
            formula = '=COM.GITHUB.AMOURSPIRIT.EXTENSION.LIBREPYTHONISTA.PYIMPL.PYC(SHEET();CELL("ADDRESS")'
            with cc.set_context(cell=cell.cell_obj, sheet_idx=sheet.sheet_index):
                found = cc.get_cell_before()
                if found:
                    formula += ";"
                    if found.sheet_idx > -1 and found.sheet_idx != cc.current_sheet_index:
                        with contextlib.suppress(Exception):
                            # maybe the sheet has been deleted
                            prev_sheet = doc.get_sheet(cc.previous_sheet_index)
                            formula += f"${prev_sheet.name}."

                    formula += f"{found.col.upper()}{found.row}"
            formula += ")"
            # cell.component.setFormula("=" + res.resolve_string("fml001"))
            cell.component.setFormula(formula)
            _ = cell.value
        except Exception as e:
            self._logger.error(f"{self.__class__.__name__} - Error: {e}")

    def _debug_dump_module_to_log(self) -> None:
        doc = CalcDoc.from_current_doc()
        PyInstance(doc).dump_module_source_code_to_log()

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
