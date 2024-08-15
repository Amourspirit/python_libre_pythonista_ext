"""To rename this module, change the module name in the project.toml ``tool.libre_pythonista.config.py_script_sheet_on_calculate`` and the filename."""

from __future__ import annotations
from typing import TYPE_CHECKING
import uno
from ooodev.events.args.event_args import EventArgs

if TYPE_CHECKING:
    from ...pythonpath.libre_pythonista_lib.log.log_inst import LogInst
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.const.event_const import CALC_FORMULAS_CALCULATED

else:
    from libre_pythonista_lib.log.log_inst import LogInst
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import CALC_FORMULAS_CALCULATED


def formulas_calc(*args):
    """
    Handle the button action event.
    """

    # no args for this event
    log = LogInst()
    SharedEvent().trigger_event(CALC_FORMULAS_CALCULATED, EventArgs(None))
    log.debug("formulas_calc() Triggered CALC_FORMULAS_CALCULATED event.")
    return


def content_changed(*args):
    """
    Handle the button action event.
    """

    # no args for this event
    log = LogInst()
    # SharedEvent().trigger_event(CALC_FORMULAS_CALCULATED, EventArgs(None))
    log.debug("content_changed() Triggered")
    return


g_exportedScripts = (
    formulas_calc,
    content_changed,
)
