from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.events.partial.events_partial import EventsPartial

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import SHEET_MODIFIED
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals, MemCache
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc
else:
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import SHEET_MODIFIED
    from libre_pythonista_lib.doc.doc_globals import DocGlobals, MemCache
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.init_commands.cmd_init_doc import CmdInitDoc

_KEY = "libre_pythonista_lib.doc.doc_monitor.DocMonitor"


def _get_cache(key: str) -> MemCache:
    """Get cache sheet from cache"""
    doc_globals = DocGlobals.get_current()
    cache = doc_globals.get_mem_cache(DocGlobals.CacheType.CALC_DOC, doc_monitor=key)
    return cache


class DocInit(LogMixin, EventsPartial):
    def __new__(cls, doc: CalcDoc) -> DocInit:
        gbl_cache = DocGlobals.get_current()
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: CalcDoc) -> None:
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        EventsPartial.__init__(self)
        self._shared_event = SharedEvent()
        self._shared_event.add_event_observers(self.event_observer)
        self._cache = _get_cache(f"{_KEY}_cache")
        self._doc = doc
        self._is_init = True

    def ensure_doc_init(self) -> None:
        """Ensure the document is initialized"""
        key = "doc_init"
        if key not in self._cache:
            handler = CmdHandler()
            cmd = CmdInitDoc(self._doc)
            handler.handle(cmd)
            self._cache[key] = True

    def is_doc_init(self) -> bool:
        """Check if the document is initialized"""
        key = "doc_init"
        return key in self._cache
