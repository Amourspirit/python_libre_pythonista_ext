from __future__ import annotations
from typing import TYPE_CHECKING
import uno
import unohelper
from com.github.amourspirit.extensions import XPy  # type: ignore

from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from .pythonpath.as_libre_office_code.dialog.py.dialog_python import DialogPython
else:
    from as_libre_office_code.dialog.py.dialog_python import DialogPython

implementation_name = "com.github.amourspirit.extension.Py"
implementation_services = ("com.sun.star.sheet.AddIn",)


class Py(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx

    def py(self) -> tuple:
        doc = CalcDoc.from_current_doc()

        dlg = DialogPython()
        dlg.show()
        # doc.msgbox("Hello from Py!", "Py", boxtype=1)
        # return (("A", "B", "C"),)
        return ((777,),)


def createInstance(ctx):
    return Py(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
