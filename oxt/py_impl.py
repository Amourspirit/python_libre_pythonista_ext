from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import os
import sys
import uno
import unohelper
from com.github.amourspirit.extensions.librepythonista import XPy  # type: ignore


from ooodev.calc import CalcDoc


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from .pythonpath.libre_pythonista_lib.dialog.py.dialog_python import DialogPython
    from .pythonpath.libre_pythonista_lib.code.py_code import PythonCode
    from .pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstances
    from .pythonpath.libre_pythonista_lib.code.py_cell import PyCell
    from .pythonpath.libre_pythonista_lib.code.code_cache import CodeCache
else:
    from libre_pythonista_lib.dialog.py.dialog_python import DialogPython
    from libre_pythonista_lib.code.py_code import PythonCode
    from libre_pythonista_lib.code.py_source_mgr import PyInstances
    from libre_pythonista_lib.code.py_cell import PyCell
    from libre_pythonista_lib.code.code_cache import CodeCache

implementation_name = "com.github.amourspirit.extension.librepythonista.PyImpl"
implementation_services = ("com.sun.star.sheet.AddIn",)


class PyImpl(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        # import debugpy

        # debugpy.listen(8550)
        # debugpy.wait_for_client()  # blocks execution until client is attached
        # print("Debug Proceeding ...")
        # it seems init is only call when the functions is first called.
        # ctx is com.sun.star.uno.XComponentContext

    def pyc(self, sheet_num: int, cell_address: str) -> tuple:
        # CodeCache should really only be used in this function.
        # It tracks the current cell and the previous cell and has listings for all code cells.
        self._logger.debug("PyImpl - pyc entered")
        try:
            self._logger.debug(f"PyImpl - pyc -sheet_num: arg {sheet_num}")
            self._logger.debug(f"PyImpl - pyc -cell_address: arg {cell_address}")
            doc = CalcDoc.from_current_doc()
            sheet_idx = sheet_num - 1
            sheet = doc.sheets[sheet_idx]
            xcell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(xcell)
            py_cell = PyCell(cell)
            cc = CodeCache()
            cc.current_sheet_index = sheet_idx
            cc.current_cell = cell.cell_obj
            self._logger.debug(f"CodeCache index: {cc.current_sheet_index}")
            self._logger.debug(f"CodeCache cell: {cc.current_cell}")
            if not py_cell.has_code():
                self._logger.debug("Py: py cell has no code")
                # prompt for code
                code = self._get_code()
                if code:
                    py_cell.save_code(code)
                    CodeCache.reset_instance()
                    cc = CodeCache()
                    cc.current_sheet_index = sheet_idx
                    cc.current_cell = cell.cell_obj
            else:
                self._logger.debug("Py: py cell has code")
            self._logger.debug(f"Is First Cell: {cc.is_first_cell()}")
            self._logger.debug(f"Is Last Cell: {cc.is_last_cell()}")
            self._logger.debug(f"Current Cell Index: {cc.get_cell_index()}")

            self._logger.debug(f"Py: py sheet_num: {sheet_num}, cell_address: {cell_address}")
        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)
        self._logger.debug("PyImpl - pyc exiting")
        return ((sheet_idx, cell_address),)

    def _get_code(self) -> str | None:
        dlg = DialogPython(self.ctx)
        self._logger.debug("Py: py displaying dialog")
        result = None
        if dlg.show():
            self._logger.debug("Py: py dialog returned with OK")
            txt = dlg.text.strip()
            if txt:
                result = dlg.text

            # if code_str:
            # inst = PyInstances(doc.get_active_sheet())
            # self._logger.debug(f"Py: py saving code")
            # code = PythonCode(ctx=self.ctx, verify_is_formula=False)
            # code.save_code(code_str)
            # self._logger.debug(f"Py: py code saved")

        else:
            self._logger.debug("Py: py dialog returned with Cancel")
        return result


def createInstance(ctx):
    return PyImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
