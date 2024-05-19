from __future__ import annotations
import uno
import unohelper
from com.sun.star.task import XJobExecutor

implementation_name = "com.github.amourspirit.extension.impl"


class PythonImpl(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, event: str):
        print("PythonImpl: trigger: event", event)


g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(PythonImpl, implementation_name, ())
