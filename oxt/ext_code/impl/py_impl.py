from __future__ import annotations
from typing import Any, Type, Tuple, cast, TYPE_CHECKING
from pathlib import Path
import contextlib
import sys
import unohelper
from com.github.amourspirit.extensions.librepythonista import XPy  # type: ignore


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck  # type: ignore

        return RequirementsCheck().run_imports_ready()
    return False


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    # this_pth = os.path.dirname(__file__)
    this_pth = str(Path(__file__).parent.parent.parent)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from com.sun.star.frame import Desktop
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc, CalcCell
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from oxt.___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from oxt.___lo_pip___.debug.break_mgr import BreakMgr
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_init import DocInit
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import (
        PYC_RULE_MATCH_DONE,
        PYC_FORMULA_ENTER,
        SHEET_CELL_MOVED,
    )

    break_mgr = BreakMgr()
else:
    _CONDITIONS_MET = _conditions_met()

    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc, CalcCell
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ___lo_pip___.debug.break_mgr import BreakMgr
        from libre_pythonista_lib.doc.doc_init import DocInit
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.const.event_const import (
            PYC_RULE_MATCH_DONE,
            PYC_FORMULA_ENTER,
            SHEET_CELL_MOVED,
        )

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("librepythonista.PyImpl2.matched_rule")
        # break_mgr.add_breakpoint("librepythonista.PyImpl2.pyc")
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PyImpl(unohelper.Base, XPy):
    IMPLE_NAME = "___lo_identifier___.PyImpl"
    SERVICE_NAMES = ("com.sun.star.sheet.AddIn",)

    @classmethod
    def get_imple(cls) -> Tuple[Type[PyImpl], str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        # this is only init one time per session. When a new document is loaded, it is not called.
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Pyc: PyImpl init")
        try:
            mgr = self.ctx.getServiceManager()
            self.desktop = cast(
                "Desktop",
                mgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx),
            )
        except Exception as e:
            self._log.error("Error: %s", e, exc_info=True)

        # it seems init is only call when the functions is first called.

    def pyc(self, sheet_num: int, cell_address: str, *args) -> Any:  # noqa: ANN002, ANN401
        if not _CONDITIONS_MET:
            self._log.error("pyc - Conditions not met")
            return None  # type: ignore
        # if not TYPE_CHECKING:
        #     try:
        #         from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item import CellItem
        #     except Exception as e:
        #         self._log.error(f"Error: {e}", exc_info=True)
        self._log.debug("pyc entered")

        break_mgr.check_breakpoint("librepythonista.PyImpl.pyc")
        value = None
        try:
            # CalcDoc.from_current_doc() should not be used here.
            # It will return the previous active document if this document is not yet ready.
            # This will cause the code to run on the wrong document.
            # This only happens when a current Calc Document is open and an existing doc is opened via File -> Open.
            # Even then it is only an issue while the document is opening.
            # However that issue cause the popup dialog to be displayed one time for each formula.
            # Getting the document from this desktop solve this issue. Mainly because the controller is None when the document is not ready.
            doc = cast(CalcDoc, Lo.current_doc)
            if doc is None:
                frame = self.desktop.getActiveFrame()
                controller = frame.getController()
                model = controller.getModel()
                # self._logger.debug(f"pyc - Doc UID: {model.RuntimeUID}")
                if model is None:
                    self._log.debug("pyc - Model is None. Attempting to get doc from current document.")
                    doc = CalcDoc.from_current_doc()
                else:
                    doc = CalcDoc.get_doc_from_component(model)
        except Exception:
            self._log.warning(
                "pyc - Could not get current document. This usually happens when the document is not fully loaded."
            )
            if self._log.is_debug:
                self._log.error("Error getting current document")
            return None

        try:
            doc_init = DocInit(doc=doc)  # singleton
            doc_init.ensure_doc_init()
            doc_init.ensure_sheet_init(doc.get_sheet(sheet_num - 1))
        except Exception as e:
            self._log.exception("Error Init Doc: %s", e)

        try:
            sheet_idx = sheet_num - 1
            sheet = doc.sheets[sheet_idx]
            x_cell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(x_cell)
            shared_event = SharedEvent(doc)

            dd = DotDict(sheet=sheet, cell=cell, event_name=PYC_FORMULA_ENTER)
            eargs = EventArgs(self)
            eargs.event_data = dd
            shared_event.trigger_event(PYC_FORMULA_ENTER, eargs)

            ci = CellItemFacade(cell)

            # calling the action method of the matched rule will return the data for the cell and

            if ci.is_source_cell():
                self._log.debug("pyc - Cell is source cell")

                # self._do_source_cell(shared_event, ci, cell)

                # if auto_update is not call then get value will act as a cached version
                # This can be uses as a static option for cell latter on.
                # see https://github.com/Amourspirit/python_libre_pythonista_ext/issues/61
                ci.auto_update()
                value = ci.get_value()
                matched_rule = ci.get_matched_rule()
                if matched_rule:
                    dd = DotDict(matched_rule=matched_rule, rule_result=value, calc_cell=cell)
                    dd.is_first_cell = ci.qry_is_first()
                    dd.is_last_cell = ci.qry_is_last()
                    eargs = EventArgs(self)
                    eargs.event_data = dd
                    shared_event.trigger_event(PYC_RULE_MATCH_DONE, eargs)
            else:
                old_new = ci.qry_cell_moved_old_new()
                if old_new:
                    self._log.debug("pyc - Cell moved.")
                    # ci_new = CellItemFacade.from_cell_addr_prop(cell)
                    old = old_new[0]
                    new = old_new[1]
                    ci.py_src_mgr.update_key(old, new)

                    dd = DotDict(
                        sheet=sheet,
                        calc_cell=cell,
                        event_name=SHEET_CELL_MOVED,
                        # is_first_cell=ci.qry_is_first(),
                        # is_last_cell=ci.qry_is_last(),
                        absolute_name=cell.component.AbsoluteName,
                        old_cell_obj=old,
                        new_cell_obj=new,
                    )
                    eargs = EventArgs(self)
                    eargs.event_data = dd
                    shared_event.trigger_event(SHEET_CELL_MOVED, eargs)
                    # ci.update_code()
                    if ci.is_source_cell():
                        self._log.debug("pyc - Cell is source cell")
                        # self._do_source_cell(shared_event, ci, cell)
                        ci.auto_update()
                        value = ci.get_value()
                        matched_rule = ci.get_matched_rule()
                        if matched_rule:
                            dd = DotDict(matched_rule=matched_rule, rule_result=value, calc_cell=cell)
                            dd.is_first_cell = ci.qry_is_first()
                            dd.is_last_cell = ci.qry_is_last()
                            eargs = EventArgs(self)
                            eargs.event_data = dd
                            shared_event.trigger_event(PYC_RULE_MATCH_DONE, eargs)
                else:
                    self._log.debug("pyc - Not a source cell. Creating Default.")
                    value = ci.add_default_control()
                    self._log.debug(
                        "pyc - Cell had no code, Created Default with value type: %s", type(value).__name__
                    )
        except Exception as e:
            self._log.exception("Error Init CellItem: %s", e)

        self._log.debug("pyc - Doc UID: %s", doc.runtime_uid)
        result = value
        self._log.debug("pyc - Done")
        return result

    def _do_source_cell(self, shared_event: SharedEvent, ci: CellItemFacade, cell: CalcCell) -> None:
        # if auto_update is not call then get value will act as a cached version
        # This can be uses as a static option for cell latter on.
        # see https://github.com/Amourspirit/python_libre_pythonista_ext/issues/61

        ci.auto_update()
        value = ci.get_value()
        matched_rule = ci.get_matched_rule()
        if matched_rule:
            dd = DotDict(matched_rule=matched_rule, rule_result=value, calc_cell=cell)
            dd.is_first_cell = ci.qry_is_first()
            dd.is_last_cell = ci.qry_is_last()
            eargs = EventArgs(self)
            eargs.event_data = dd
            shared_event.trigger_event(PYC_RULE_MATCH_DONE, eargs)


g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PyImpl.get_imple())
