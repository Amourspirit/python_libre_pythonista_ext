from __future__ import annotations
from typing import TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
import unohelper
from com.sun.star.frame import XStatusListener
from ...log.log_inst import LogInst

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.frame import FeatureStateEvent


class EditStatusListener(XStatusListener, unohelper.Base):
    def __init__(self, sheet: str, cell: str):
        XStatusListener.__init__(self)
        unohelper.Base.__init__(self)
        self._sheet = sheet
        self._cell = cell
        self._log = LogInst()

    @override
    def statusChanged(self, State: FeatureStateEvent):
        self._log.debug(f"EditStatusListener statusChanged: {State}")
        # event.IsEnabled = False

    @override
    def disposing(self, Source: EventObject):
        self._log.debug("EditStatusListener disposing()")
