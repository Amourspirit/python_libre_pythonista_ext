from __future__ import annotations
from typing import TYPE_CHECKING
import uno
import unohelper
from com.sun.star.frame import XStatusListener
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.frame import FeatureStateEvent


class EditStatusListener(XStatusListener, unohelper.Base):
    def __init__(self, sheet: str, cell: str):
        XStatusListener.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._log = LogInst()

    def statusChanged(self, event: FeatureStateEvent):
        self._log.debug(f"EditStatusListener statusChanged: {event}")
        # event.IsEnabled = False

    def disposing(self, source):
        self._log.debug("EditStatusListener disposing()")
