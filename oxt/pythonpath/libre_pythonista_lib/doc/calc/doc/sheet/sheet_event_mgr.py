from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcSheet


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.lp_listeners.listener_sheet_calculated import (
        ListenerSheetCalculated,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.lp_listeners.listener_after_calculate_cells_moved import (
        ListenerAfterCalculateCellsMoved,
    )
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cache.calc.sheet.sheet_cache import get_sheet_cache
    from libre_pythonista_lib.doc.calc.doc.sheet.lp_listeners.listener_sheet_calculated import (
        ListenerSheetCalculated,
    )
    from libre_pythonista_lib.doc.calc.doc.sheet.lp_listeners.listener_after_calculate_cells_moved import (
        ListenerAfterCalculateCellsMoved,
    )

_KEY = "pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.sheet_event_mgr.SheetEventMgr"

# SheetEventMgr for new sheets are init via sheet.listen.code_sheet_activation_listener.CodeSheetActivationListener
# Original Sheets are init via cq.cmd.calc.init_commands.cmd_init_sheet.CmdInitSheet


class SheetEventMgr(LogMixin):
    def __new__(cls, sheet: CalcSheet) -> SheetEventMgr:
        sheet_cache = get_sheet_cache(sheet)
        if _KEY in sheet_cache:
            return sheet_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        sheet_cache[_KEY] = inst
        return inst

    def __init__(self, sheet: CalcSheet) -> None:
        """
        Constructor

        Args:
            src_mgr (PySourceManager): The source manager to manage events for.
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._sheet = sheet
        self._lp_listeners = []
        self._init_events()
        self.log.debug("Init done for sheet: %s", sheet.name)
        self._is_init = True

    def _init_events(self) -> None:
        self._lp_listeners.append(ListenerSheetCalculated(self._sheet))
        self._lp_listeners.append(ListenerAfterCalculateCellsMoved(self._sheet))
