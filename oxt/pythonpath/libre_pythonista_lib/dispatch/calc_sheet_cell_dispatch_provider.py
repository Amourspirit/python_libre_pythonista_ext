from __future__ import annotations
from typing import Any, cast, Dict, Tuple, TYPE_CHECKING
from urllib.parse import parse_qs

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.frame import XDispatchProviderInterceptor
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.util import URL
from com.sun.star.frame import DispatchDescriptor

from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

# from ooodev.calc import CalcDoc
from ..const import (
    CS_PROTOCOL,
    UNO_DISPATCH_CODE_EDIT_MB,
    PATH_CODE_DEL,
    PATH_CELL_SELECT,
    PATH_CELL_SELECT_RECALC,
    UNO_DISPATCH_DF_STATE,
    UNO_DISPATCH_DS_STATE,
    UNO_DISPATCH_DATA_TBL_STATE,
    UNO_DISPATCH_PY_OBJ_STATE,
)

from ..const.event_const import GBL_DOC_CLOSING, LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
from ..log.log_inst import LogInst
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config

# Imports are lazy imports to avoid potential failure, especially during startup when the secondary required modules may not be loaded.
# If not lazy import then a failing import could cause all dispatches here to fail.
# Also many commands import other modules that may not be common, so lazy import is used to avoid unnecessary imports.


class CalcSheetCellDispatchProvider(unohelper.Base, XDispatchProviderInterceptor):
    """
    Dispatch Provider Interceptor.

    This class needs to be kept alive as long as the dispatch provider is in use.
    For this reason this class is a singleton.

    Calling the ``dispose()`` method will release the singleton instance.
    """

    _instances = {}

    def __new__(cls, doc: OfficeDocumentT, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        # sc = Lo.xscript_context
        # doc = sc.getDocument()
        # uid = doc.RuntimeUID

        uid = doc.runtime_uid
        key = f"dpi_{uid}"
        if key not in cls._instances:
            inst = super(CalcSheetCellDispatchProvider, cls).__new__(cls, *args, **kwargs)
            inst._initialized = False
            inst._key = key
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, doc: OfficeDocumentT) -> None:
        if getattr(self, "_initialized", False):
            return
        self._master = cast(XDispatchProvider, None)
        self._slave = cast(XDispatchProvider, None)
        self._config = Config()
        self._initialized = True
        self._key: str
        self._doc = doc

    # def _convert_query_to_dict(self, query: str):
    #     return parse_qs(query)

    def _convert_query_to_dict(self, query_string: str) -> Dict[str, str]:
        parsed_query = parse_qs(query_string)
        return {k: v[0] for k, v in parsed_query.items()}

    @override
    def getMasterDispatchProvider(self) -> XDispatchProvider:
        """
        access to the master XDispatchProvider of this interceptor
        """
        return self._master

    @override
    def getSlaveDispatchProvider(self) -> XDispatchProvider:
        """
        access to the slave XDispatchProvider of this interceptor
        """
        return self._slave

    @override
    def setMasterDispatchProvider(self, NewSupplier: XDispatchProvider) -> None:  # noqa: N803
        """
        sets the master XDispatchProvider, which may forward calls to its XDispatchProvider.queryDispatch() to this dispatch provider.
        """
        self._master = NewSupplier

    @override
    def setSlaveDispatchProvider(self, NewDispatchProvider: XDispatchProvider) -> None:  # noqa: N803
        """
        sets the slave XDispatchProvider to which calls to XDispatchProvider.queryDispatch() can be forwarded under control of this dispatch provider.
        """
        self._slave = NewDispatchProvider

    def _query_process_cs_protocol(
        self,
        URL: URL,  # noqa: N803
        TargetFrameName: str,  # noqa: N803
        SearchFlags: int,  # noqa: N803
        log: LogInst,
    ) -> XDispatch | None:  # type: ignore
        try:
            from ..menus import menu_util as mu
        except ImportError:
            log.exception("menu_util import error")
            raise
        cs_url = mu.get_url_from_command(URL.Complete)
        if log.is_debug:
            log.debug("_query_process_cs_protocol()")
            log.debug(str(cs_url))
        se = SharedEvent()

        if cs_url.Main == UNO_DISPATCH_CODE_EDIT_MB:
            is_experiential = self._config.lp_settings.experimental_editor
            if is_experiential:
                try:
                    from .dispatch_edit_py_cell_wv import (
                        DispatchEditPyCellWv as DispatchEditPyCell,
                    )
                except ImportError:
                    log.exception("DispatchEditPyCellWv import error")
                    raise
            else:
                try:
                    from .dispatch_edit_py_cell_mb import (
                        DispatchEditPyCellMb as DispatchEditPyCell,
                    )
                except ImportError:
                    log.exception("DispatchEditPyCellMb import error")
                    raise

            try:
                args = self._convert_query_to_dict(cs_url.Arguments)
                in_thread = args.pop("in_thread", "0") == "1"
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(
                    url=cs_url,
                    cmd=cs_url.Complete,
                    doc=self._doc,
                    in_thread=in_thread,
                    experiential_edit=is_experiential,
                    **args,
                )

                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    if is_experiential:
                        log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchEditPyCellWv")
                    else:
                        log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchEditPyCellMb")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif cs_url.Path == PATH_CODE_DEL:
            try:
                from .dispatch_del_py_cell import DispatchDelPyCell
            except ImportError:
                log.exception("DispatchDelPyCell import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchDelPyCell")
                result = DispatchDelPyCell(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        elif cs_url.Path == PATH_CELL_SELECT_RECALC:
            try:
                from .dispatch_cell_select_recalc import DispatchCellSelectRecalc
            except ImportError:
                log.exception("DispatchCellSelectRecalc import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchCellSelectRecalc")
                result = DispatchCellSelectRecalc(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {cs_url.Main}")
                return None

        elif cs_url.Path == PATH_CELL_SELECT:
            try:
                from .dispatch_cell_select import DispatchCellSelect
            except ImportError:
                log.exception("DispatchCellSelect import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchCellSelect")
                result = DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        if cs_url.Main == UNO_DISPATCH_DF_STATE:
            try:
                from .dispatch_toggle_df_state import DispatchToggleDfState
            except ImportError:
                log.exception("DispatchToggleDfState import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchToggleDfState")
                result = DispatchToggleDfState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)

                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        if cs_url.Main == UNO_DISPATCH_DS_STATE:
            try:
                from .dispatch_toggle_series_state import DispatchToggleSeriesState
            except ImportError:
                log.exception("DispatchToggleSeriesState import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchToggleSeriesState")
                result = DispatchToggleSeriesState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        elif cs_url.Main == UNO_DISPATCH_DATA_TBL_STATE:
            try:
                from .dispatch_toggle_data_tbl_state import DispatchToggleDataTblState
            except ImportError:
                log.exception("DispatchToggleDataTblState import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetCellDispatchProvider.queryDispatch: returning DispatchToggleDataTblState")
                result = DispatchToggleDataTblState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        elif cs_url.Main == UNO_DISPATCH_PY_OBJ_STATE:
            try:
                from .dispatch_py_obj_state import DispatchPyObjState
            except ImportError:
                log.exception("DispatchPyObjState import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyObjState")
                result = DispatchPyObjState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", cs_url.Main)
                return None

    @override
    def queryDispatch(  # type: ignore
        self,
        URL: URL,  # noqa: N803
        TargetFrameName: str,  # noqa: N803
        SearchFlags: int,  # noqa: N803
    ) -> XDispatch | None:  # type: ignore
        """
        Searches for an XDispatch for the specified URL within the specified target frame.
        """
        if URL.Protocol == "slot:":
            # not really sure if this is necessary but there have been reports in the past
            # of crashes without this check.
            return None

        log = LogInst()
        log.debug("CalcSheetCellDispatchProvider.queryDispatch: %s", URL.Complete)

        if URL.Protocol == CS_PROTOCOL:
            return self._query_process_cs_protocol(URL, TargetFrameName, SearchFlags, log)

        return self._slave.queryDispatch(URL, TargetFrameName, SearchFlags)

    def queryDispatches(self, Requests: Tuple[DispatchDescriptor, ...]) -> Tuple[XDispatch, ...]:  # noqa: N802, N803
        """
        Actually this method is redundant to XDispatchProvider.queryDispatch() to avoid multiple remote calls.

        It's not allowed to pack it - because every request must match to its real result. Means: don't delete NULL entries inside this list.
        """
        result = []
        for item in Requests:
            result.append(self.queryDispatch(item.FeatureURL, item.FrameName, item.SearchFlags))
        return tuple(result)

    def dispose(self) -> None:
        if self._key in CalcSheetCellDispatchProvider._instances:
            del CalcSheetCellDispatchProvider._instances[self._key]

    @classmethod
    def has_instance(cls, doc: OfficeDocumentT) -> bool:
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        doc.runtime_uid
        key = f"dpi_{doc.runtime_uid}"
        return key in cls._instances


def _on_doc_closing(src: Any, event: EventArgs) -> None:  # noqa: ANN401
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"dpi_{uid}"
    if key in CalcSheetCellDispatchProvider._instances:
        del CalcSheetCellDispatchProvider._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
