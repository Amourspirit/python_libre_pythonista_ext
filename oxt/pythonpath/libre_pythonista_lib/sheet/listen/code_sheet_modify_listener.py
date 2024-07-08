from __future__ import annotations
from typing import Any, TYPE_CHECKING

import uno
import unohelper
from com.sun.star.util import XModifyListener
from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ...cell.cell_mgr import CellMgr
from ...const.event_const import GBL_DOC_CLOSING
from ...event.shared_event import SharedEvent
from ...const.event_const import SHEET_MODIFIED

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CodeSheetModifyListener(XModifyListener, unohelper.Base):
    """Singleton class for Code Sheet Modify Listener."""

    _instances = {}

    def __new__(cls, inst_name: str) -> CodeSheetModifyListener:
        key = cls._get_key(inst_name)
        if key not in cls._instances:
            inst = super().__new__(cls)
            inst._is_init = False
            inst._inst_name = key
            cls._instances[key] = inst
        return cls._instances[key]

    @classmethod
    def _get_key(cls, inst_name: str) -> str:
        return f"{Lo.current_doc.runtime_uid}_uid_{inst_name}"

    def __init__(
        self,
        inst_name: str,
    ) -> None:
        if getattr(self, "_is_init", False):
            return
        XModifyListener.__init__(self)
        unohelper.Base.__init__(self)
        self._inst_name: str  # = inst_name
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._is_init = True

    def modified(self, event: EventObject) -> None:
        """
        Is called when something changes in the object.

        Due to such an event, it may be necessary to update views or controllers.

        The source of the event may be the content of the object to which the listener
        is registered.
        """
        # event.Source: implementationName=ScTableSheetObj
        # event.Source: com.sun.star.sheet.Spreadsheet
        self._log.debug("Sheet Modified. Raising SHEET_MODIFIED event.")
        # if self._log.is_debug:
        #     self._log.debug(str(event.Source))
        event_args = EventArgs(self)
        event_args.event_data = DotDict(src=self, event=event)
        SharedEvent().trigger_event(SHEET_MODIFIED, event_args)

    def disposing(self, event: EventObject) -> None:
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """
        if self._log is not None:
            self._log.debug("Disposing")
        if self._inst_name in CodeSheetModifyListener._instances:
            del CodeSheetModifyListener._instances[self._inst_name]
        setattr(self, "_log", None)  # avoid type checker complaining about log being none.

    def __del__(self) -> None:
        if self._log is not None:
            self._log.debug("Deleted")
        if self._inst_name in CodeSheetModifyListener._instances:
            del CodeSheetModifyListener._instances[self._inst_name]
        setattr(self, "_log", None)

    @classmethod
    def reset_instance(cls, inst_name: str = "") -> None:
        key_inst = cls._get_key(inst_name)
        if not inst_name:
            for key in list(cls._instances.keys()):
                if key.startswith(key_inst):
                    del cls._instances[key]
            return
        if key_inst in cls._instances:
            del cls._instances[inst_name]
        return None

    @classmethod
    def has_listener(cls, inst_name: str) -> bool:
        key_inst = cls._get_key(inst_name)
        return key_inst in cls._instances

    @classmethod
    def get_listener(cls, inst_name: str) -> CodeSheetModifyListener:
        key_inst = cls._get_key(inst_name)
        return cls._instances.get(key_inst, None)


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    uid = str(event.event_data.uid)
    key_start = f"{uid}_uid_"
    for key in list(CodeSheetModifyListener._instances.keys()):
        if key.startswith(key_start):
            del CodeSheetModifyListener._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
