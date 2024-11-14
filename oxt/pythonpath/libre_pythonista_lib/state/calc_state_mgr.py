"""
Manages the state of the document and Sheets.
"""

from __future__ import annotations
from typing import Any, cast, Dict, TYPE_CHECKING
from ooodev.calc import CalcDoc
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict
from ooodev.io.sfa import Sfa
from ooodev.utils.props import Props

from ..const.event_const import (
    OXT_INIT,
    GBL_DOC_CLOSING,
    DOCUMENT_EVENT,
    LP_DOC_EVENTS_ENSURED,
)
from ..utils.singleton_base import SingletonBase
from ..event.shared_event import SharedEvent

# from ..code.py_source_mgr import PyInstance

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.config import Config


# sheet.listen.sheet_activation_listener.SheetActivationListener triggers the event


class CalcStateMgr(SingletonBase):
    """
    Contains Document State Properties.
    """

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_is_init", False):
            return
        self._doc = doc
        # if not hasattr(self, "_props"):
        #     self._props: Dict[str, Any] = {}
        # if not hasattr(self, "_log"):
        #     self._log = OxtLogger(log_name=self.__class__.__name__)
        # if not hasattr(self, "_config"):
        #     self._config = Config()

        if not hasattr(self, "_is_first_init"):
            self._log = OxtLogger(log_name=self.__class__.__name__)
            with self._log.noindent():
                self._log.debug(f"Initializing {self.__class__.__name__}")
            self._config = Config()
            self._sfa = Sfa()
            self._lp_code_dir = (
                f"vnd.sun.star.tdoc:/{self._doc.runtime_uid}/{self._config.lp_code_dir}"
            )
            self._props: Dict[str, Any] = {}
            self._se = SharedEvent(doc)
            self._calc_event_ensured = False
            self._fn_on_lp_doc_events_ensured = self._on_lp_doc_events_ensured
            # CalcDocMgr is a singleton and it creates and instance of CalcStateMgr.
            self._se.subscribe_event(
                LP_DOC_EVENTS_ENSURED, self._fn_on_lp_doc_events_ensured
            )
            self._is_first_init = True

    def _init_state_mgr(self) -> None:
        self._log.debug("_init_state_mgr()")
        self._fn_on_calc_doc_new_view = self._on_calc_doc_new_view
        self._fn_on_calc_doc_closing = self._on_calc_doc_closing
        self._fn_on_calc_doc_event = self._on_calc_doc_event
        self._se.subscribe_event(OXT_INIT, self._fn_on_calc_doc_new_view)
        self._se.subscribe_event(GBL_DOC_CLOSING, self._fn_on_calc_doc_closing)
        self._se.subscribe_event(DOCUMENT_EVENT, self._fn_on_calc_doc_event)
        self._is_init = True

    def _on_calc_doc_new_view(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_calc_doc_new_view() Calc New View")
        if not self._is_init:
            self._init_state_mgr()
        self._is_init = True

    def _on_lp_doc_events_ensured(self, src: Any, event: EventArgs) -> None:
        self._log.debug("_on_lp_doc_events_ensured() Entered.")
        # runtime_uid
        if isinstance(event.event_data, DotDict) and hasattr(
            event.event_data, "run_id"
        ):
            uid = event.event_data.run_id
        else:
            uid = self.runtime_uid  # noqa # type: ignore
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
        """
        Makes a key for the state manager.

        Key is in the format: uid_{uid}_{key} and is different for each document.
        """
        if uid:
            return f"uid_{uid}_{key}"

        return f"uid_{self._doc.runtime_uid}_{key}"

    def _clear_keys(self, uid: str) -> None:
        prefix = f"uid_{uid}_"
        keys = [k for k in self._props.keys() if k.startswith(prefix)]
        for key in keys:
            del self._props[key]

    def is_import_available(self, module_name: str) -> bool:
        try:
            __import__(module_name)
        except (ModuleNotFoundError, ImportError):
            return False
        return True

    @property
    def is_pythonista_doc(self) -> bool:
        """Gets if the document is a Pythonista Document (has code)."""
        # if not getattr(self, "_is_init", False):
        #     return False
        key = self._make_key("is_pythonista_doc")
        if key in self._props:
            return bool(self._props[key])
        else:
            result = self._sfa.exists(self._lp_code_dir)
            if result:
                self._log.debug(
                    "is_pythonista_doc() Code Folder %s Exists",
                    self._config.lp_code_dir,
                )
                self._props[key] = True
            else:
                self._log.debug(
                    "is_pythonista_doc() Code Folder %s Does Not Exist",
                    self._config.lp_code_dir,
                )
            return result
            # inst = PyInstance(self._doc)
            # return inst.has_code()

    @is_pythonista_doc.setter
    def is_pythonista_doc(self, value: bool) -> None:
        """Sets if the document is a Pythonista Document (has code)."""
        # if not getattr(self, "_is_init", False):
        #     return
        key = self._make_key("is_pythonista_doc")
        if value:
            self._props[key] = True
        else:
            if key in self._props:
                del self._props[key]

    @property
    def is_new_document(self) -> bool:
        """
        Checks if the current document is a new, unsaved document.

        Returns:
            bool: True if the document is new and unsaved, False otherwise.
        """
        # https://wiki.openoffice.org/wiki/Documentation/DevGuide/OfficeDev/Component/Models
        doc_args = self._doc.component.getArgs()
        args_dic = Props.props_to_dot_dict(doc_args)
        return args_dic.URL == ""

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

    @property
    def is_imports2_ready(self) -> bool:
        try:
            return self._imports2_ready
        except AttributeError:
            self._imports2_ready = all(
                self.is_import_available(imp) for imp in self._config.run_imports2
            )
        return self._imports2_ready
