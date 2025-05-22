from __future__ import annotations
from typing import cast, Dict, Tuple, TYPE_CHECKING, Union
from urllib.parse import parse_qs
import contextlib


import unohelper
from com.sun.star.frame import XDispatchProviderInterceptor
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.util import URL
from com.sun.star.frame import DispatchDescriptor

from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from typing_extensions import override
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.config import Config
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from oxt.pythonpath.libre_pythonista_lib.const.event_const import (
        LP_DISPATCHED_CMD,
        LP_DISPATCHING_CMD,
    )
    from oxt.pythonpath.libre_pythonista_lib.const import (
        CS_PROTOCOL,
        PATH_CODE_EDIT_MB,
        PATH_CODE_DEL,
        PATH_CELL_SELECT,
        PATH_CELL_SELECT_RECALC,
        PATH_DF_STATE,
        PATH_DS_STATE,
        PATH_DATA_TBL_STATE,
    )
else:
    from ___lo_pip___.config import Config
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.event.shared_event import SharedEvent
    from libre_pythonista_lib.const.event_const import LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
    from libre_pythonista_lib.const import (
        CS_PROTOCOL,
        PATH_CODE_EDIT_MB,
        PATH_CODE_DEL,
        PATH_CELL_SELECT,
        PATH_CELL_SELECT_RECALC,
        PATH_DF_STATE,
        PATH_DS_STATE,
        PATH_DATA_TBL_STATE,
    )

    def override(func):  # noqa: ANN001, ANN201
        return func

# Imports are lazy imports to avoid potential failure, especially during startup when the secondary required modules may not be loaded.
# If not lazy import then a failing import could cause all dispatches here to fail.
# Also many commands import other modules that may not be common, so lazy import is used to avoid unnecessary imports.

_KEY = "libre_pythonista_lib.dispatch.calc_sheet_cell_dispatch_provider.CalcSheetCellDispatchProvider"


class CalcSheetCellDispatchProvider(XDispatchProviderInterceptor, LogMixin, unohelper.Base):
    """
    Dispatch Provider Interceptor.

    This class needs to be kept alive as long as the dispatch provider is in use.
    For this reason this class is a singleton.

    Calling the ``dispose()`` method will release the singleton instance.
    """

    def __new__(cls, doc: OfficeDocumentT, *args, **kwargs) -> CalcSheetCellDispatchProvider:  # noqa: ANN002, ANN003
        gbl_cache = DocGlobals.get_current()
        if _KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_KEY]

        inst = super().__new__(cls)
        inst._initialized = False

        gbl_cache.mem_cache[_KEY] = inst
        return inst

    def __init__(self, doc: OfficeDocumentT) -> None:
        if getattr(self, "_initialized", False):
            return
        XDispatchProviderInterceptor.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._master = cast(XDispatchProvider, None)
        self._slave = cast(XDispatchProvider, None)
        self._config = Config()
        self._initialized = True
        self._doc = doc

    # def _convert_query_to_dict(self, query: str):
    #     return parse_qs(query)

    def _convert_query_to_dict(self, query_string: str) -> Dict[str, str]:
        parsed_query = parse_qs(query_string)
        return {k: v[0] for k, v in parsed_query.items()}

    @override
    def getMasterDispatchProvider(self) -> XDispatchProvider:  # noqa: N802
        """
        access to the master XDispatchProvider of this interceptor
        """
        return self._master

    @override
    def getSlaveDispatchProvider(self) -> XDispatchProvider:  # noqa: N802
        """
        access to the slave XDispatchProvider of this interceptor
        """
        return self._slave

    @override
    def setMasterDispatchProvider(self, NewSupplier: XDispatchProvider) -> None:  # noqa: N802, N803
        """
        sets the master XDispatchProvider, which may forward calls to its XDispatchProvider.queryDispatch() to this dispatch provider.
        """
        self._master = NewSupplier

    @override
    def setSlaveDispatchProvider(self, NewDispatchProvider: XDispatchProvider) -> None:  # noqa: N802, N803
        """
        sets the slave XDispatchProvider to which calls to XDispatchProvider.queryDispatch() can be forwarded under control of this dispatch provider.
        """
        self._slave = NewDispatchProvider

    def _query_process_cs_protocol(
        self,
        URL: URL,  # noqa: N803
        TargetFrameName: str,  # noqa: N803
        SearchFlags: int,  # noqa: N803
    ) -> Union[XDispatch, None]:  # type: ignore
        try:
            if TYPE_CHECKING:
                from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.menus import menu_util as mu
            else:
                from libre_pythonista_lib.doc.calc.doc.menus import menu_util as mu
        except ImportError:
            self.log.exception("menu_util import error")
            raise
        cs_url = mu.get_url_from_command(URL.Complete)
        if self.log.is_debug:
            self.log.debug("_query_process_cs_protocol()")
            self.log.debug(str(cs_url))
        se = SharedEvent()

        if cs_url.Path == PATH_CODE_EDIT_MB:
            is_experiential = self._config.lp_settings.experimental_editor
            if is_experiential:
                try:
                    from .dispatch_edit_py_cell_wv import (
                        DispatchEditPyCellWv as DispatchEditPyCell,
                    )
                except ImportError:
                    self.log.exception("DispatchEditPyCellWv import error")
                    raise
            else:
                try:
                    from .dispatch_edit_py_cell_mb2 import (
                        DispatchEditPyCellMb2 as DispatchEditPyCell,
                    )
                except ImportError:
                    self.log.exception("DispatchEditPyCellMb2 import error")
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

                with self.log.indent(True):
                    if is_experiential:
                        self.log.debug("queryDispatch: returning DispatchEditPyCellWv")
                    else:
                        self.log.debug("queryDispatch: returning DispatchEditPyCellMb2")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif cs_url.Path == PATH_CODE_DEL:
            try:
                from .dispatch_del_py_cell2 import DispatchDelPyCell2
            except ImportError:
                self.log.exception("DispatchDelPyCell2 import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchDelPyCell2")
                result = DispatchDelPyCell2(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        elif cs_url.Path == PATH_CELL_SELECT_RECALC:
            try:
                from .dispatch_cell_select_recalc import DispatchCellSelectRecalc
            except ImportError:
                self.log.exception("DispatchCellSelectRecalc import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchCellSelectRecalc")
                result = DispatchCellSelectRecalc(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception(f"Dispatch Error: {cs_url.Main}")
                return None

        elif cs_url.Path == PATH_CELL_SELECT:
            try:
                from .dispatch_cell_select import DispatchCellSelect
            except ImportError:
                self.log.exception("DispatchCellSelect import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchCellSelect")
                result = DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        if cs_url.Path == PATH_DF_STATE:
            try:
                from .dispatch_toggle_df_state2 import DispatchToggleDfState2
            except ImportError:
                self.log.exception("DispatchToggleDfState2 import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchToggleDfState2")
                result = DispatchToggleDfState2(sheet=args["sheet"], cell=args["cell"], uid=self._doc.runtime_uid)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)

                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        if cs_url.Path == PATH_DS_STATE:
            try:
                from .dispatch_toggle_series_state2 import DispatchToggleSeriesState2
            except ImportError:
                self.log.exception("DispatchToggleSeriesState2 import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchToggleSeriesState2")
                result = DispatchToggleSeriesState2(sheet=args["sheet"], cell=args["cell"], uid=self._doc.runtime_uid)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", cs_url.Main)
                return None

        elif cs_url.Path == PATH_DATA_TBL_STATE:
            try:
                from .dispatch_toggle_data_tbl_state2 import DispatchToggleDataTblState2
            except ImportError:
                self.log.exception("DispatchToggleDataTblState2 import error")
                raise
            try:
                args = self._convert_query_to_dict(cs_url.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=cs_url, cmd=cs_url.Complete, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with self.log.indent(True):
                    self.log.debug("queryDispatch: returning DispatchToggleDataTblState2")
                result = DispatchToggleDataTblState2(sheet=args["sheet"], cell=args["cell"], uid=self._doc.runtime_uid)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                self.log.exception("Dispatch Error: %s", cs_url.Main)
                return None

    @override
    def queryDispatch(  # type: ignore  # noqa: N802
        self,
        URL: URL,  # noqa: N803
        TargetFrameName: str,  # noqa: N803
        SearchFlags: int,  # noqa: N803
    ) -> Union[XDispatch, None]:  # type: ignore
        """
        Searches for an XDispatch for the specified URL within the specified target frame.
        """
        if URL.Protocol == "slot:":
            # not really sure if this is necessary but there have been reports in the past
            # of crashes without this check.
            return None

        if URL.Protocol == CS_PROTOCOL:
            self.log.debug("queryDispatch: %s", URL.Complete)
            return self._query_process_cs_protocol(URL, TargetFrameName, SearchFlags)

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
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_KEY]

    @classmethod
    def has_instance(cls, doc: OfficeDocumentT) -> bool:
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        gbl_cache = DocGlobals.get_current()
        return _KEY in gbl_cache.mem_cache
