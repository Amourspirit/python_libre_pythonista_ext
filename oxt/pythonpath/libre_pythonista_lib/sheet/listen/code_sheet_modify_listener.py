from __future__ import annotations
from typing import TYPE_CHECKING

import uno
import unohelper
from com.sun.star.util import XModifyListener
from ooodev.calc import CalcDoc
from ...cell.cell_mgr import CellMgr

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class CodeSheetModifyListener(unohelper.Base, XModifyListener):
    """Singleton class for Code Sheet Modify Listener."""

    _instances = {}

    def __new__(cls, inst_name: str) -> CodeSheetModifyListener:
        if inst_name not in cls._instances:
            inst = super().__new__(cls)
            inst._is_init = False
            cls._instances[inst_name] = inst
        return cls._instances[inst_name]

    def __init__(
        self,
        inst_name: str,
    ) -> None:
        if getattr(self, "_is_init", False):
            return
        super().__init__()
        self._inst_name = inst_name
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._is_init = True

    def modified(self, event: EventObject) -> None:
        """
        Is called when something changes in the object.

        Due to such an event, it may be necessary to update views or controllers.

        The source of the event may be the content of the object to which the listener
        is registered.
        """
        try:
            self._log.debug("Modified - Resetting instance.")
            doc = CalcDoc.from_current_doc()
            cm = CellMgr(doc)
            # cm.reset_instance()
            cm.reset_py_inst()
        except Exception:
            self._log.error("Error resetting instance", exc_info=True)

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
        if not inst_name:
            cls._instances.clear()
            return
        if inst_name in cls._instances:
            del cls._instances[inst_name]
        return None

    @classmethod
    def has_listener(cls, inst_name: str) -> bool:
        return inst_name in cls._instances
