from __future__ import annotations

import uno
import unohelper
from com.github.amourspirit.extensions.librepythonista import XTesting  # type: ignore


implementation_name = "com.github.amourspirit.extension.librepythonista.TestingImpl"
implementation_services = ("com.sun.star.sheet.AddIn",)


class TestingImpl(unohelper.Base, XTesting):
    def __init__(self, ctx):
        self.ctx = ctx

    def testing(self, sheet_num: int, cell_address: str):
        return f"{sheet_num}:{cell_address}"


def createInstance(ctx):
    return TestingImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
