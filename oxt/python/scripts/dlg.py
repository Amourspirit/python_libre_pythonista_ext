from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import uno

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext

    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.dialog.options.log_opt import LogOpt

    XSCRIPTCONTEXT: XScriptContext
else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.dialog.options.log_opt import LogOpt


def dlg_test(*args):
    """
    Handle the button action event.
    """
    log_opt = LogOpt()
    log_opt.show()
