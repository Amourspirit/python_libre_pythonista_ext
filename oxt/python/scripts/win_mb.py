from __future__ import annotations
from typing import TYPE_CHECKING
import uno

if TYPE_CHECKING:
    from com.sun.star.script.provider import XScriptContext
    from com.sun.star.awt import ActionEvent

    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.dialog.py.dialog_mb import DialogMb

    XSCRIPTCONTEXT: XScriptContext
else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.dialog.py.dialog_mb import DialogMb


def show_win_mb(*args):
    """
    Handle the button action event.
    """

    log = LogInst()
    log.debug("show_win_mb debug")
    try:
        mb = DialogMb(XSCRIPTCONTEXT)
    except Exception:
        log.error("show_win_mb: Error", exc_info=True)
