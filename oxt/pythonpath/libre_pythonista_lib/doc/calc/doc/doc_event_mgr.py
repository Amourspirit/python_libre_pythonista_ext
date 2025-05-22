from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcDoc


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.lp_listeners.listener_py_src_mgr_mod_states_init_updated import (
        ListenerPySrcMgrModStatesInitUpdated,
    )
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.doc.calc.doc.lp_listeners.listener_py_src_mgr_mod_states_init_updated import (
        ListenerPySrcMgrModStatesInitUpdated,
    )

_KEY = "pythonpath.libre_pythonista_lib.doc.calc.doc.doc_event_mgr.DocEventMgr"


class DocEventMgr(LogMixin):
    def __new__(cls, doc: CalcDoc) -> DocEventMgr:
        doc_cache = DocGlobals.get_current_mem_cache()
        if _KEY in doc_cache:
            return doc_cache[_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        doc_cache[_KEY] = inst
        return inst

    def __init__(self, doc: CalcDoc) -> None:
        """
        Constructor

        Args:
            doc (CalcDoc): The Calc document to manage events for.
        """
        if getattr(self, "_is_init", False):
            return
        LogMixin.__init__(self)
        self._doc = doc
        self._lp_listeners = []
        self._init_events()
        self.log.debug("Init done for doc: %s", doc.runtime_uid)
        self._is_init = True

    def _init_events(self) -> None:
        self._lp_listeners.append(ListenerPySrcMgrModStatesInitUpdated(self._doc))
