# -*- coding: utf-8 -*-
from __future__ import annotations
import uno
import unohelper
from org.openoffice.sheet.addin import XPy
from ooodev.calc import CalcDoc


class Py(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx

    def py(self) -> tuple:
        doc = CalcDoc.from_current_doc()
        doc.msgbox("Hello from Py!", "Py", boxtype=1)
        # return (("A", "B", "C"),)
        return ((777,),)


def createInstance(ctx):
    return Py(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    createInstance,
    "org.openoffice.Py",
    ("com.sun.star.sheet.AddIn",),
)
