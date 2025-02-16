from __future__ import annotations
from typing import TYPE_CHECKING
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.util import XModifyListener
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.events.lo_events import LoEvents
from ooodev.loader import Lo

from ...ex.exceptions import SingletonKeyError
from ...event.shared_event import SharedEvent
from ...const.event_const import SHEET_MODIFIED

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin

_CODE_SHEET_MODIFY_LISTENER_KEY = (
    "libre_pythonista_lib.sheet.listen.code_sheet_modify_listener.CodeSheetModifyListener"
)


class CodeSheetModifyListener(XModifyListener, LogMixin, unohelper.Base):
    """Singleton class for Code Sheet Modify Listener."""

    def __new__(cls, inst_name: str) -> CodeSheetModifyListener:
        gbl_cache = DocGlobals.get_current()
        key = cls._get_key(inst_name, gbl_cache.runtime_uid)
        if (
            _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache
            and key in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]
        ):
            return gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][key]

        inst = super().__new__(cls)
        inst._inst_name = key
        inst._runtime_uid = gbl_cache.runtime_uid
        inst._is_init = False

        gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY] = {key: inst}
        return inst

    @classmethod
    def _get_key(cls, inst_name: str, runtime_uid: str) -> str:
        eargs = EventArgs(cls)
        eargs.event_data = DotDict(class_name=cls.__name__, key="", inst_name=inst_name)
        LoEvents().trigger("LibrePythonistaCodeSheetModifyListenerGetKey", eargs)
        if eargs.event_data.key:
            return eargs.event_data.key
        try:
            return f"{runtime_uid}_uid_{inst_name}"
        except Exception as e:
            raise SingletonKeyError(
                f"Error getting single key for class name: {cls.__name__} with inst_name: {inst_name}"
            ) from e

    def __init__(self, inst_name: str) -> None:
        if getattr(self, "_is_init", False):
            return
        XModifyListener.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._inst_name: str
        self._runtime_uid: str
        self._trigger_events = True
        self._is_init = True

    def set_trigger_state(self, trigger: bool) -> None:
        """
        Sets the state of the trigger events.

        Args:
            trigger (bool): The state to set for the trigger events. If True,
                trigger events will be enabled. If False, they will be disabled.
        Returns:
            None
        """
        # removing this listener from the document does not seem to work.
        # by setting the trigger to False, we can prevent the listener from firing.
        self._trigger_events = trigger

    def get_trigger_state(self) -> bool:
        """
        Returns the current state of the trigger events.

        Returns:
            bool: The state of the trigger events.
        """

        return self._trigger_events

    @override
    def modified(self, aEvent: EventObject) -> None:  # noqa: N803
        """
        Is called when something changes in the object.

        Due to such an event, it may be necessary to update views or controllers.

        The source of the event may be the content of the object to which the listener
        is registered.
        """
        if not self._trigger_events:
            self.log.debug("Trigger events is False. Not raising SHEET_MODIFIED event.")
            return
        # event.Source: implementationName=ScTableSheetObj
        # event.Source: com.sun.star.sheet.Spreadsheet
        self.log.debug("Sheet Modified. Raising SHEET_MODIFIED event.")
        # if self._log.is_debug:
        #     self._log.debug(str(event.Source))
        event_args = EventArgs(self)
        event_args.event_data = DotDict(src=self, event=aEvent)
        SharedEvent().trigger_event(SHEET_MODIFIED, event_args)

    @override
    def disposing(self, Source: EventObject) -> None:  # noqa: N803
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """

        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if not _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache:
                return

            if self._inst_name in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]:
                del gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][self._inst_name]

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if not _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache:
                return

            if self._inst_name in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]:
                del gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][self._inst_name]

    @classmethod
    def reset_instance(cls, inst_name: str = "") -> None:
        gbl_cache = DocGlobals.get_current()
        if not _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache:
            return

        key_inst = cls._get_key(inst_name, gbl_cache.runtime_uid)
        if not inst_name:
            for key in list(gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY].keys()):
                if key.startswith(key_inst):
                    del gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][key]
            return

        if key_inst in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]:
            del gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][key_inst]
        return None

    @classmethod
    def has_listener(cls, inst_name: str) -> bool:
        gbl_cache = DocGlobals.get_current()
        key_inst = cls._get_key(inst_name, gbl_cache.runtime_uid)

        if not _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache:
            return False
        return key_inst in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]

    @classmethod
    def get_listener(cls, inst_name: str) -> CodeSheetModifyListener:
        gbl_cache = DocGlobals.get_current()
        key = cls._get_key(inst_name, gbl_cache.runtime_uid)
        if not _CODE_SHEET_MODIFY_LISTENER_KEY in gbl_cache.mem_cache:
            raise SingletonKeyError(f"Key {_CODE_SHEET_MODIFY_LISTENER_KEY} not found in cache.")
        if key in gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY]:
            return gbl_cache.mem_cache[_CODE_SHEET_MODIFY_LISTENER_KEY][key]
        raise SingletonKeyError(f"Key {key} not found in cache.")
