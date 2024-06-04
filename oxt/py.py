from __future__ import annotations
from typing import cast, TYPE_CHECKING
import os
import sys
import uno
import unohelper
from com.github.amourspirit.extensions import XPy  # type: ignore


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

implementation_name = "com.github.amourspirit.extension.Py"
implementation_services = ("com.sun.star.sheet.AddIn",)


class Py(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        # import debugpy

        # debugpy.listen(8550)
        # debugpy.wait_for_client()  # blocks execution until client is attached
        # print("Debug Proceeding ...")
        # it seems init is only call when the functions is first called.
        # ctx is com.sun.star.uno.XComponentContext

    def py(self) -> tuple:
        # get access to the Link List that manages the module for all cells.
        # add/edit or remove this cells python from the Link List.
        # Link list needs to update all down stream python cells.
        print(dir(self))

        doc = CalcDoc.from_current_doc()

        # returns $A1$1 no matter the current cell.
        # print("call function", doc.call_fun("CELL", "address"))

        sel = doc.get_current_selection()

        # breakpoint()

        if sel is None:
            print("no current selection")
            return (("No current selection",),)
        if not hasattr(sel, "getImplementationName"):
            print("no getImplementationName")
            return (("No getImplementationName",),)
        impl_name = cast(str, sel.getImplementationName())  # type: ignore
        print(impl_name)
        if impl_name != "ScCellObj":
            print("not a cell object")
            return (("Not a cell object",),)
        addr = sel.CellAddress  # type: ignore
        print("Address", f"Column {addr.Column}, Row {addr.Row}")
        return (("Col", addr.Column, "Row", addr.Row),)

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
    return Py(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
