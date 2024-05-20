from __future__ import annotations
from typing import TYPE_CHECKING
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
    from .pythonpath.as_libre_office_code.dialog.py.dialog_python import DialogPython
    from .pythonpath.as_libre_office_code.code.py_code import PythonCode
else:
    from as_libre_office_code.dialog.py.dialog_python import DialogPython
    from as_libre_office_code.code.py_code import PythonCode

implementation_name = "com.github.amourspirit.extension.Py"
implementation_services = ("com.sun.star.sheet.AddIn",)


class Py(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)

    def py(self) -> tuple:
        doc = CalcDoc.from_current_doc()

        dlg = DialogPython(self.ctx)
        self._logger.debug("Py: py displaying dialog")
        if dlg.show():
            self._logger.debug("Py: py dialog returned with OK")
            code_str = dlg.text
            if code_str:
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
