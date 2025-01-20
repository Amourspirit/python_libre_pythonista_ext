from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from pathlib import Path
import contextlib
import os
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
    from ooodev.calc import CalcDoc
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ooodev.utils.data_type.col_obj import ColObj
    from ...___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ...___lo_pip___.config import Config
    from ...___lo_pip___.debug.break_mgr import BreakMgr
    from ...pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr
    from ...pythonpath.libre_pythonista_lib.code.cell_cache import CellCache
    from ...pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.pyc_rules import (
        PycRules,
    )
    from ...pythonpath.libre_pythonista_lib.cell.lpl_cell import LplCell  # noqa: F401
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.const.event_const import (
        PYC_RULE_MATCH_DONE,
        PYC_FORMULA_ENTER,
    )
    from ...pythonpath.libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr

    break_mgr = BreakMgr()
else:
    _CONDITIONS_MET = _conditions_met()

    if _CONDITIONS_MET:
        from ooodev.calc import CalcDoc
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from ooodev.utils.data_type.col_obj import ColObj
        from libre_pythonista_lib.cell.cell_mgr import CellMgr
        from libre_pythonista_lib.cell.result_action.pyc.rules.pyc_rules import PycRules
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.code.cell_cache import CellCache
        from libre_pythonista_lib.const.event_const import (
            PYC_RULE_MATCH_DONE,
            PYC_FORMULA_ENTER,
        )
        from libre_pythonista_lib.state.calc_state_mgr import CalcStateMgr
        from ___lo_pip___.debug.break_mgr import BreakMgr

        # Initialize the breakpoint manager
        break_mgr = BreakMgr()
        # break_mgr.add_breakpoint("librepythonista.PyImpl.matched_rule")
        # break_mgr.add_breakpoint("librepythonista.PyImpl.pyc")
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class PyImpl(unohelper.Base, XPy):
    IMPLE_NAME = "___lo_identifier___.PyImpl"
    SERVICE_NAMES = ("com.sun.star.sheet.AddIn",)

    @classmethod
    def get_imple(cls) -> tuple:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        # this is only init one time per session. When a new document is loaded, it is not called.
        self.ctx = ctx
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._log.debug("Py: PyImpl init")
        try:
            mgr = self.ctx.getServiceManager()
            self.desktop = cast(
                "Desktop",
                mgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx),
            )
        except Exception as e:
            self._log.error(f"Error: {e}", exc_info=True)

        # it seems init is only call when the functions is first called.

    def pyc(self, sheet_num: int, cell_address: str, *args) -> Any:  # noqa: ANN002, ANN401
        if not _CONDITIONS_MET:
            self._log.error("pyc - Conditions not met")
            return None  # type: ignore
        self._log.debug("pyc entered")

        break_mgr.check_breakpoint("librepythonista.PyImpl.pyc")

        try:
            # CalcDoc.from_current_doc() should not be used here.
            # It will return the previous active document if this document is not yet ready.
            # This will cause the code to run on the wrong document.
            # This only happens when a current Calc Document is open and an existing doc is opened via File -> Open.
            # Even then it is only an issue while the document is opening.
            # However that issue cause the popup dialog to be displayed one time for each formula.
            # Getting the document from this desktop solve this issue. Mainly because the controller is None when the document is not ready.
            frame = self.desktop.getActiveFrame()
            controller = frame.getController()
            model = controller.getModel()
            # self._logger.debug(f"pyc - Doc UID: {model.RuntimeUID}")
            doc = CalcDoc.get_doc_from_component(model)
        except Exception:
            self._log.warning(
                "pyc - Could not get current document. This usually happens when the document is not fully loaded."
            )
            return None

        result = None
        try:
            self._log.debug("pyc - Doc UID: %s", doc.runtime_uid)
            calc_state_mgr = CalcStateMgr(doc)
            if not calc_state_mgr.is_job_loading_finished:
                self._log.debug("pyc - Loading Job not finished. Returning.")
                return None

            key = f"LIBRE_PYTHONISTA_DOC_{doc.runtime_uid}"
            if key not in os.environ:
                # if len(sheet.draw_page) == 0:
                # if there are no draw pages for the sheet then they are not yet loaded. Return None, and expect a recalculation to take place when the document is fully loaded.
                self._log.debug("pyc - Not yet loaded. Returning.")
                CellMgr.reset_instance(doc)
                return None  # type: ignore
            cm = CellMgr(doc)
            shared_event = SharedEvent(doc)

            # cm.set_global_var("PY_ARGS", args)
            # cc = CellCache(doc)
            sheet_idx = sheet_num - 1
            self._log.debug("pyc - sheet_num: arg %i", sheet_num)
            self._log.debug("pyc - cell_address: arg %s", cell_address)
            if args:
                self._log.debug("pyc - args count: %i", len(args))

            sheet = doc.sheets[sheet_idx]
            x_cell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(x_cell)
            self._log.debug(
                "pyc - Cell %s for sheet index %i has custom properties: %s",
                cell.cell_obj,
                cell.cell_obj.sheet_idx,
                cell.has_custom_properties(),
            )
            dd = DotDict(sheet=sheet, cell=cell, event_name=PYC_FORMULA_ENTER)
            eargs = EventArgs(self)
            eargs.event_data = dd
            shared_event.trigger_event(PYC_FORMULA_ENTER, eargs)

            if cm.has_cell(cell_obj=cell.cell_obj):
                self._log.debug("pyc - py cell has code")
            else:
                # if not py_cell.has_code():
                self._log.debug("pyc - py %s cell has no code", cell.cell_obj)

                # this could be a result of rows or columns being inserted.
                # if the cell is A5 and a row is inserted above then the cell is now A6.
                # By the time this method is called it will see Cell A6 and not A5 when the row is inserted.
                # This means the cell may indeed have code and just not be in the current cm cache.
                code_handled = False
                if not TYPE_CHECKING:
                    from libre_pythonista_lib.cell.lpl_cell import LplCell
                lp_cell = LplCell(cell)
                if lp_cell.has_code_name_prop:
                    self._log.debug(
                        "pyc - py %s cell already has code. May be a row or column as been inserted.", cell.cell_obj
                    )
                    # If the cell is move this is not the place to update the cell properties.
                    # If done here only the current cell would be updated.
                    # Once this block runs it update the CellMgr and therefore all
                    # subsequent moved cells will be in and cm so this next part would not run.
                    #
                    # if lp_cell.has_cell_moved:
                    #     self._logger.debug(f"pyc - py {cell.cell_obj} cell has Moved.")
                    #     lp_cell.cell_prop_addr = cell.cell_obj
                    #     self._logger.debug(f"pyc - py {cell.cell_obj} Update Cell address property.")

                    code_handled = True
                    lp_cell.reset_py_instance()
                    CellMgr.reset_instance(doc)
                    cm = CellMgr(doc)
                    if lp_cell.has_cell_moved:
                        self._log.debug("pyc - py %s cell has Moved.", cell.cell_obj)
                        cm.update_sheet_cell_addr_prop(sheet_idx)

                if not code_handled:
                    cm.add_source_code(source_code="", cell_obj=cell.cell_obj)

            # resetting is handled by the CodeSheetModifyListener
            # if cm.is_first_cell(cell_obj=cell.cell_obj):
            #     cm.reset_py_inst()
            # else:
            #     cm.update_from_cell_obj(cell_obj=cell.cell_obj)

            py_src = cm.get_py_src(cell_obj=cell.cell_obj)
            # py_src = py_inst[cc.current_cell]
            pyc_rules = PycRules()
            matched_rule = pyc_rules.get_matched_rule(cell=cell, data=py_src.dd_data)
            if matched_rule:
                if self._log.is_debug:
                    self._log.debug("pyc - Matched Rule: %s", matched_rule)
                # calling the action method of the matched rule will return the data for the cell and
                # set the custom property for the cell that is used by CodeCellListener to raise an event that is then
                # handled by the CellMgr which uses CtlMgr to assign the control to the cell.
                break_mgr.check_breakpoint("librepythonista.PyImpl.matched_rule")
                rule_result = matched_rule.action()
                cm.add_cell_control_from_pyc_rule(rule=matched_rule)

                cell_cache = CellCache(doc)
                dd = DotDict(matched_rule=matched_rule, rule_result=rule_result, calc_cell=cell)
                dd.is_first_cell = cell_cache.is_first_cell(cell=cell.cell_obj, sheet_idx=sheet_idx)
                dd.is_last_cell = cell_cache.is_last_cell(cell=cell.cell_obj, sheet_idx=sheet_idx)
                eargs = EventArgs(self)
                eargs.event_data = dd
                shared_event.trigger_event(PYC_RULE_MATCH_DONE, eargs)

                self._log.debug("pyc - Done")
                return rule_result

            else:
                self._log.debug("pyc - No matched rule")

            result = py_src.value if isinstance(py_src.value, tuple) else ((py_src.value,),)

        except Exception as e:
            self._log.error("Error: %s", e, exc_info=True)
            raise
        self._log.debug("pyc exiting")
        # return ((sheet_idx, cell_address),)
        # return (("a", "b"), (1.0, 2.0))
        self._log.debug("pyc - result:\n%s", result)
        if isinstance(result, tuple):
            # try setting an array.
            width = len(result[0])
            height = len(result)
            cell_obj = cell.cell_obj
            rng_obj = cell_obj.get_range_obj()
            rng_obj += ColObj.from_int(width - 1)
            rng_obj += height - 1
            cfg = Config()
            key = f"{cfg.cell_cp_prefix}modify_trigger_event"
            cell.set_custom_property(key, "cell_table_data")
            self._log.debug(f"pyc - Table Range: {rng_obj}")
            # rng = sheet.get_range(range_obj=rng_obj)
            # rng.component.setArrayFormula(cell.component.getFormula())

            # return result
        self._log.debug("pyc - Done")
        return result


g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*PyImpl.get_imple())
