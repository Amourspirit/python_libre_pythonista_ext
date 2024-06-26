from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
from pathlib import Path
import contextlib
import os
import sys
import uno
import unohelper
from com.github.amourspirit.extensions.librepythonista import XPy  # type: ignore


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck

        return RequirementsCheck().run_imports_ready()
    return False


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    # this_pth = os.path.dirname(__file__)
    this_pth = str(Path(__file__).parent.parent)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from com.sun.star.frame import Desktop
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.utils.data_type.cell_obj import CellObj
    from ooodev.utils.data_type.range_obj import RangeObj
    from ooodev.utils.data_type.col_obj import ColObj
    from ooodev.exceptions import ex as mEx
    from ..___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ..___lo_pip___.config import Config
    from ..pythonpath.libre_pythonista_lib.dialog.py.dialog_python import DialogPython
    from ..pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr
    from ..pythonpath.libre_pythonista_lib.cell.result_action.pyc.rules.pyc_rules import PycRules

else:
    _CONDITIONS_MET = _conditions_met()

    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.utils.data_type.cell_obj import CellObj
        from ooodev.utils.data_type.range_obj import RangeObj
        from ooodev.utils.data_type.col_obj import ColObj
        from ooodev.exceptions import ex as mEx
        from libre_pythonista_lib.dialog.py.dialog_python import DialogPython
        from libre_pythonista_lib.cell.cell_mgr import CellMgr
        from libre_pythonista_lib.cell.result_action.pyc.rules.pyc_rules import PycRules
    from ___lo_pip___.config import Config
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


implementation_name = "com.github.amourspirit.extension.librepythonista.PyImpl"
implementation_services = ("com.sun.star.sheet.AddIn",)


class PyImpl(unohelper.Base, XPy):
    def __init__(self, ctx: Any):
        # this is only init one time per session. When a new document is loaded, it is not called.
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("Py: PyImpl init")
        try:
            mgr = self.ctx.getServiceManager()
            self.desktop = cast("Desktop", mgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx))
        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)

        # it seems init is only call when the functions is first called.

    def pyc(self, sheet_num: int, cell_address: str, *args) -> Any:
        if not _CONDITIONS_MET:
            self._logger.error("pyc - Conditions not met")
            return None  # type: ignore
        self._logger.debug("pyc entered")
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
            self._logger.warning(
                "pyc - Could not get current document. This usually happens when the document is not fully loaded."
            )
            return None
        result = None
        try:
            self._logger.debug(f"pyc - Doc UID: {doc.runtime_uid}")
            key = f"LIBRE_PYTHONISTA_DOC_{doc.runtime_uid}"
            if not key in os.environ:
                # if len(sheet.draw_page) == 0:
                # if there are no draw pages for the sheet then they are not yet loaded. Return None, and expect a recalculation to take place when the document is fully loaded.
                self._logger.debug("pyc - Not yet loaded. Returning.")
                CellMgr.reset_instance(doc)
                return None  # type: ignore
            cm = CellMgr(doc)
            # cm.set_global_var("PY_ARGS", args)
            # cc = CellCache(doc)
            sheet_idx = sheet_num - 1
            self._logger.debug(f"pyc - sheet_num: arg {sheet_num}")
            self._logger.debug(f"pyc - cell_address: arg {cell_address}")
            if args:
                self._logger.debug(f"pyc -args: {args}")

            sheet = doc.sheets[sheet_idx]
            xcell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(xcell)
            self._logger.debug(
                f"pyc - Cell {cell.cell_obj} for sheet index {cell.cell_obj.sheet_idx} has custom properties: {cell.has_custom_properties()}"
            )

            if not cm.has_cell(cell_obj=cell.cell_obj):

                # if not py_cell.has_code():
                self._logger.debug("pyc - py cell has no code")
                # prompt for code
                code = self._get_code()
                if code:
                    # When source code is added to CellMgr is will add CodeCellListener listener to this cell.
                    cm.add_source_code(source_code=code, cell_obj=cell.cell_obj)
                    # now the listener has been added to the cell, return a result and recalculate the cell.
                else:
                    self._logger.debug("pyc - No code entered")
                    return None
            else:
                self._logger.debug("pyc - py cell has code")
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
                if self._logger.is_debug:
                    self._logger.debug(f"pyc - Matched Rule: {matched_rule}")
                # calling the action method of the matched rule will return the data for the cell and
                # set the custom property for the cell that is used by CodeCellListener to raise an event that is then
                # handled by the CellMgr which uses CtlMgr to assign the control to the cell.
                rule_result = matched_rule.action()
                cm.add_cell_control_from_pyc_rule(rule=matched_rule)
                return rule_result

            else:
                self._logger.debug("pyc - No matched rule")

            if isinstance(py_src.value, tuple):
                result = py_src.value
            else:
                result = ((py_src.value,),)

        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)
            raise
        self._logger.debug("pyc exiting")
        # return ((sheet_idx, cell_address),)
        # return (("a", "b"), (1.0, 2.0))
        self._logger.debug(f"pyc - result:\n{result}")
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
            self._logger.debug(f"pyc - Table Range: {rng_obj}")
            # rng = sheet.get_range(range_obj=rng_obj)
            # rng.component.setArrayFormula(cell.component.getFormula())

            # return result
        return result

    def _get_code(self) -> str | None:
        dlg = DialogPython(self.ctx)
        self._logger.debug("Py - _get_code() py displaying dialog")
        result = None
        if dlg.show():
            self._logger.debug("Py - _get_code() - py dialog returned with OK")
            txt = dlg.text.strip()
            if txt:
                result = dlg.text

        else:
            self._logger.debug("Py - _get_code() - py dialog returned with Cancel")
        return result


def createInstance(ctx):
    return PyImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
