from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
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
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

if TYPE_CHECKING:
    _CONDITIONS_MET = True
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.exceptions import ex as mEx
    from .___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .pythonpath.libre_pythonista_lib.dialog.py.dialog_python import DialogPython

    # from .pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstance
    # from .pythonpath.libre_pythonista_lib.code.cell_cache import CellCache
    from .pythonpath.libre_pythonista_lib.cell.cell_mgr import CellMgr
else:
    _CONDITIONS_MET = _conditions_met()

    if _CONDITIONS_MET:
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.exceptions import ex as mEx
        from libre_pythonista_lib.dialog.py.dialog_python import DialogPython

        # from libre_pythonista_lib.code.py_source_mgr import PyInstance
        # from libre_pythonista_lib.code.cell_cache import CellCache
        from libre_pythonista_lib.cell.cell_mgr import CellMgr
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


implementation_name = "com.github.amourspirit.extension.librepythonista.PyImpl"
implementation_services = ("com.sun.star.sheet.AddIn",)


class PyImpl(unohelper.Base, XPy):
    def __init__(self, ctx):
        # this is only init one time per session. When a new document is loaded, it is not called.
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._logger.debug("Py: PyImpl init")
        # PyInstance.reset_instance()
        # CellCache.reset_instance()
        # it seems init is only call when the functions is first called.
        # ctx is com.sun.star.uno.XComponentContext

    def pyc(self, sheet_num: int, cell_address: str, *args) -> Any:
        # CellCache should really only be used in this function.
        # It tracks the current cell and the previous cell and has listings for all code cells.
        # pprint(self.ctx.getElementNames())
        if not _CONDITIONS_MET:
            self._logger.error("pyc - Conditions not met")
            return None  # type: ignore
        self._logger.debug("pyc entered")
        try:
            _ = Lo.current_doc
            doc = CalcDoc.from_current_doc()
            self._logger.debug(f"Doc UID: {doc.runtime_uid}")

        except mEx.MissingInterfaceError:
            self._logger.warning(
                "pyc - MissingInterfaceError from Lo.current_doc. Returning and expecting a recalculation to take place when document is fully loaded."
            )
            return ((sheet_num, cell_address),)
        result = None
        try:
            key = f"LIBRE_PYTHONISTA_DOC_{doc.runtime_uid}"
            if not key in os.environ:
                # if len(sheet.draw_page) == 0:
                # if there are no draw pages for the sheet then they are not yet loaded. Return None, and expect a recalculation to take place when the document is fully loaded.
                self._logger.debug("pyc - Not yet loaded. Returning.")
                CellMgr.reset_instance(doc)
                return None  # type: ignore
            cm = CellMgr(doc)
            # cc = CellCache(doc)
            sheet_idx = sheet_num - 1
            self._logger.debug(f"pyc - sheet_num: arg {sheet_num}")
            self._logger.debug(f"pyc - cell_address: arg {cell_address}")
            if args:
                self._logger.debug(f"pyc -args: {args}")

            sheet = doc.sheets[sheet_idx]
            xcell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(xcell)
            self._logger.debug(f"pyc - Cell {cell.cell_obj} has custom properties: {cell.has_custom_properties()}")

            # py_cell = PyCell(cell)
            # cc = CellCache(doc)
            # cc_len = len(cc.code_cells[sheet_idx])
            # if cc_len == 0:
            #     CellCache.reset_instance(doc)
            #     cc = CellCache(doc)
            # self._logger.debug(f"pyc - Length of cc: {len(cc.code_cells[sheet_idx])}")
            # py_inst = PyInstance(doc)
            # cc_prop = cc.code_prop
            # cc.current_sheet_index = sheet_idx
            # cc.current_cell = cell.cell_obj
            # self._logger.debug(f"CellCache index: {cc.current_sheet_index}")
            # self._logger.debug(f"CellCache cell: {cc.current_cell}")
            if not cm.has_cell(cell_obj=cell.cell_obj):

                # if not py_cell.has_code():
                self._logger.debug("Py: py cell has no code")
                # prompt for code
                code = self._get_code()
                if code:
                    # py_cell.save_code(code)
                    cm.add_source_code(source_code=code, cell_obj=cell.cell_obj)
                    # cc.current_sheet_index = sheet_idx
                    # cc.current_cell = cell.cell_obj
                    # PyInstance.reset_instance(doc)
                    # py_inst = PyInstance(doc)
                    # py_inst.update_all()
            else:
                self._logger.debug("Py: py cell has code")
            # self._logger.debug(f"Is First Cell: {cc.is_first_cell()}")
            # self._logger.debug(f"Is Last Cell: {cc.is_last_cell()}")
            # self._logger.debug(f"Current Cell Index: {cc.get_cell_index()}")

            self._logger.debug(f"Py: py sheet_num: {sheet_num}, cell_address: {cell_address}")
            # py_inst = PyInstance(doc)
            if cm.is_first_cell(cell_obj=cell.cell_obj):
                cm.reset_py_inst()
            py_src = cm.get_py_src(cell_obj=cell.cell_obj)
            # py_src = py_inst[cc.current_cell]
            if isinstance(py_src.value, tuple):
                result = py_src.value
            else:
                result = ((py_src.value,),)

        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)
            raise
        self._logger.debug("pyc exiting")
        # return ((sheet_idx, cell_address),)
        return result

    def _get_code(self) -> str | None:
        dlg = DialogPython(self.ctx)
        self._logger.debug("Py: py displaying dialog")
        result = None
        if dlg.show():
            self._logger.debug("Py: py dialog returned with OK")
            txt = dlg.text.strip()
            if txt:
                result = dlg.text

        else:
            self._logger.debug("Py: py dialog returned with Cancel")
        return result


def createInstance(ctx):
    return PyImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)