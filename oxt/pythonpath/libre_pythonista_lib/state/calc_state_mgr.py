"""
Manages the state of the document and Sheets.
"""

from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
from ooodev.calc import CalcDoc
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const.event_const import OXT_INIT, GBL_DOC_CLOSING, DOCUMENT_EVENT
from ..utils.singleton_base import SingletonBase
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


# sheet.listen.sheet_activation_listener.SheetActivationListener triggers the event


class CalcStateMgr(SingletonBase):
    """
    Contains Document State Properties.
    """

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_is_init", False):
            return
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.noindent():
            self._log.debug(f"Initializing {self.__class__.__name__}")
        self._doc = doc
        self._props: Dict[str, Any] = {}
        self._se = SharedEvent(doc)
        self._calc_event_ensured = False
        self._fn_on_calc_doc_new_view = self._on_calc_doc_new_view
        self._fn_on_calc_doc_closing = self._on_calc_doc_closing
        self._fn_on_calc_doc_event = self._on_calc_doc_event
        self._se.subscribe_event(OXT_INIT, self._fn_on_calc_doc_new_view)
        self._se.subscribe_event(GBL_DOC_CLOSING, self._fn_on_calc_doc_closing)
        self._se.subscribe_event(DOCUMENT_EVENT, self._fn_on_calc_doc_event)
        self._is_init = True

    def _on_calc_doc_new_view(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_doc_new_view() Calc New View")
        dd = cast(DotDict, event.event_data)
        uid = dd.run_id
        key = self._make_key("new_view", uid)
        self._props[key] = True

    def _on_calc_doc_closing(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_doc_closing() Calc Doc Closing")
        dd = cast(DotDict, event.event_data)
        uid = dd.run_id
        self._clear_keys(uid)

    def _on_calc_doc_event(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_doc_event() Calc Doc Event")
        dd = cast(DotDict, event.event_data)
        event_name = dd.event_name
        if event_name == "OnLoad":
            key = self._make_key("doc_loaded", dd.run_id)
            if not self._props.get(key, False):
                self._props[key] = True
                self._log.debug("_on_calc_doc_event () Document Loaded")
            return
        if event_name == "OnUnload":
            key = self._make_key("doc_loaded", dd.run_id)
            if key in self._props:
                del self._props[key]
                self._log.debug("_on_calc_doc_event () Document Unloaded")
            return

    def _make_key(self, key: str, uid: str = "") -> str:
        if uid:
            return f"uid_{uid}_{key}"

        return f"uid_{self._doc.runtime_uid}_{key}"

    def _clear_keys(self, uid: str) -> None:
        prefix = f"uid_{uid}_"
        keys = [k for k in self._props.keys() if k.startswith(prefix)]
        for key in keys:
            del self._props[key]

    @property
    def is_view_loaded(self) -> bool:
        key = self._make_key("new_view")
        return self._props.get(key, False)

    @property
    def is_doc_loaded(self) -> bool:
        key = self._make_key("doc_loaded")
        return self._props.get(key, False)

    @property
    def is_oxt_init(self) -> bool:
        key = self._make_key("oxt_init")
        return self._props.get(key, False)

    @is_oxt_init.setter
    def is_oxt_init(self, value: bool) -> None:
        key = self._make_key("oxt_init")
        if value:
            self._props[key] = True
        else:
            if key in self._props:
                del self._props[key]
