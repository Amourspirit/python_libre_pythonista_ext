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
else:
    from libre_pythonista_lib.dialog.py.dialog_python import DialogPython
    from libre_pythonista_lib.code.py_code import PythonCode
    from libre_pythonista_lib.code.py_source_mgr import PyInstances

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

        try:
            doc = CalcDoc.from_current_doc()
            sheet_idx = sheet_num - 1
            sheet = doc.sheets[sheet_idx]
            xcell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(xcell)
            cell.set_custom_property("Python", "Python")
            self._logger.debug(f"Py: py sheet_num: {sheet_num}, cell_address: {cell_address}")
        except Exception as e:
            self._logger.error(f"Error: {e}")
        return ((sheet_idx, cell_address),)

        dlg = DialogPython(self.ctx)
        self._logger.debug("Py: py displaying dialog")
        if dlg.show():
            self._logger.debug("Py: py dialog returned with OK")
            code_str = dlg.text
            if code_str:
                # inst = PyInstances(doc.get_active_sheet())
                self._logger.debug(f"Py: py saving code")
                code = PythonCode(ctx=self.ctx, verify_is_formula=False)
                code.save_code(code_str)
                self._logger.debug(f"Py: py code saved")
        else:
            self._logger.debug("Py: py dialog returned with Cancel")
        # doc.msgbox("Hello from Py!", "Py", boxtype=1)
        # return (("A", "B", "C"),)
        # return ((777,),)
        result = f"\u2774\u2775 {dlg.res_resolver.resolve_string('py001')}"
        self._logger.debug(f"Py: py returning {result}")
        return ((result,),)


def createInstance(ctx):
    return PyImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
