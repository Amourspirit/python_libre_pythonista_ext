from __future__ import annotations
from typing import TYPE_CHECKING
import os
import sys
import uno
import unohelper
from com.sun.star.task import XJobExecutor


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

if TYPE_CHECKING:
    from pythonpath.as_libre_office_code.res.res_resolver import ResResolver
else:
    from as_libre_office_code.res.res_resolver import ResResolver

implementation_name = "___lo_identifier___.impl"


class PythonImpl(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, event: str):
        print("PythonImpl: trigger: event", event)
        try:
            res = ResResolver(self.ctx)
            msg = res.resolve_string("title10")
            print(msg)
        except Exception as e:
            print(e)


g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(PythonImpl, implementation_name, ("com.sun.star.task.Job",))
