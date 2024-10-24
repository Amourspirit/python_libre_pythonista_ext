from __future__ import annotations
from typing import Any, cast, Tuple, TYPE_CHECKING
from urllib.parse import parse_qs
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno
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
    UNO_DISPATCH_CODE_EDIT,
    UNO_DISPATCH_CODE_EDIT_MB,
    UNO_DISPATCH_DF_STATE,
    UNO_DISPATCH_DS_STATE,
    UNO_DISPATCH_DATA_TBL_STATE,
    UNO_DISPATCH_CODE_DEL,
    UNO_DISPATCH_PY_OBJ_STATE,
    UNO_DISPATCH_CELL_SELECT,
    UNO_DISPATCH_CELL_SELECT_RECALC,
    UNO_DISPATCH_DF_CARD,
    UNO_DISPATCH_DATA_TBL_CARD,
    UNO_DISPATCH_SEL_RNG,
    UNO_DISPATCH_ABOUT,
    UNO_DISPATCH_LOG_WIN,
    UNO_DISPATCH_CELL_CTl_UPDATE,
    UNO_DISPATCH_PIP_PKG_INSTALL,
    UNO_DISPATCH_PIP_PKG_UNINSTALL,
    UNO_DISPATCH_PIP_PKG_INSTALLED,
    UNO_DISPATCH_PIP_PKG_LINK,
    UNO_DISPATCH_PIP_PKG_UNLINK,
    UNO_DISPATCH_PYC_FORMULA,
    UNO_DISPATCH_PYC_FORMULA_DEP,
)

from ..const.event_const import GBL_DOC_CLOSING, LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
from ..log.log_inst import LogInst
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT

# Imports are lazy imports to avoid potential failure, especially during startup when the secondary required modules may not be loaded.
# If not lazy import then a failing import could cause all dispatches here to fail.
# Also many commands import other modules that may not be common, so lazy import is used to avoid unnecessary imports.


class DispatchProviderInterceptor(unohelper.Base, XDispatchProviderInterceptor):
    """
    Dispatch Provider Interceptor.

    This class needs to be kept alive as long as the dispatch provider is in use.
    For this reason this class is a singleton.

    Calling the ``dispose()`` method will release the singleton instance.
    """

    _instances = {}

    def __new__(cls, doc: OfficeDocumentT, *args, **kwargs):
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        # sc = Lo.xscript_context
        # doc = sc.getDocument()
        # uid = doc.RuntimeUID

        uid = doc.runtime_uid
        key = f"dpi_{uid}"
        if not key in cls._instances:
            inst = super(DispatchProviderInterceptor, cls).__new__(cls, *args, **kwargs)
            inst._initialized = False
            inst._key = key
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, doc: OfficeDocumentT):
        if getattr(self, "_initialized", False):
            return
        self._master = cast(XDispatchProvider, None)
        self._slave = cast(XDispatchProvider, None)
        self._initialized = True
        self._key: str
        self._doc = doc

    # def _convert_query_to_dict(self, query: str):
    #     return parse_qs(query)

    def _convert_query_to_dict(self, query: str):
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

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
    def setMasterDispatchProvider(self, NewSupplier: XDispatchProvider) -> None:
        """
        sets the master XDispatchProvider, which may forward calls to its XDispatchProvider.queryDispatch() to this dispatch provider.
        """
        self._master = NewSupplier

    @override
    def setSlaveDispatchProvider(self, NewDispatchProvider: XDispatchProvider) -> None:
        """
        sets the slave XDispatchProvider to which calls to XDispatchProvider.queryDispatch() can be forwarded under control of this dispatch provider.
        """
        self._slave = NewDispatchProvider

    @override
    def queryDispatch(self, URL: URL, TargetFrameName: str, SearchFlags: int) -> XDispatch | None:  # type: ignore
        """
        Searches for an XDispatch for the specified URL within the specified target frame.
        """
        if URL.Protocol == "slot:":
            # not really sure if this is necessary but there have been reports in the past
            # of crashes without this check.
            return None

        log = LogInst()
        # this next line adds over 1000 lines to the log file
        # log.debug(f"DispatchProviderInterceptor.queryDispatch: {url.Complete}")

        # example log entries
        # 2024-06-19 21:23:54,872 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:Quit
        # 2024-06-19 21:23:54,872 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:About
        # 2024-06-19 21:23:54,873 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:PrinterSetup
        # 2024-06-19 21:23:54,873 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:SafeMode
        # 2024-06-19 21:23:54,874 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:DevelopmentToolsDockingWindow

        # def handle_dispatched_cmd(event: CancelEventArgs) -> None:

        se = SharedEvent(doc=self._doc)
        if URL.Main == UNO_DISPATCH_PYC_FORMULA_DEP:
            try:
                from .dispatch_pyc_formula_dep import DispatchPycFormulaDep
            except ImportError:
                log.exception("DispatchPycFormulaDep import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PYC_FORMULA_DEP, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPycFormulaDep")

                result = DispatchPycFormulaDep()
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PYC_FORMULA:
            try:
                from .dispatch_pyc_formula import DispatchPycFormula
            except ImportError:
                log.exception("DispatchPycFormula import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PYC_FORMULA, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPycFormula")

                result = DispatchPycFormula()
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CODE_EDIT:
            try:
                from .dispatch_edit_py_cell import DispatchEditPyCell
            except ImportError:
                log.exception("DispatchEditPyCell import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CODE_EDIT, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCell")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CODE_EDIT_MB:
            try:
                from .dispatch_edit_py_cell_mb import DispatchEditPyCellMb
            except ImportError:
                log.exception("DispatchEditPyCellMb import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)
                in_thread = args.pop("in_thread", "0") == "1"
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CODE_EDIT_MB, doc=self._doc, in_thread=in_thread, **args)

                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCellMb")
                result = DispatchEditPyCellMb(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_LOG_WIN:
            try:
                from .dispatch_log_window import DispatchLogWindow
            except ImportError:
                log.exception("DispatchLogWindow import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)
                in_thread = args.pop("in_thread", "0") == "1"

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_LOG_WIN, doc=self._doc, in_thread=in_thread, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchLogWindow")
                result = DispatchLogWindow(in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_DF_STATE:
            try:
                from .dispatch_toggle_df_state import DispatchToggleDfState
            except ImportError:
                log.exception("DispatchToggleDfState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_DF_STATE, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleDfState")
                result = DispatchToggleDfState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)

                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_DS_STATE:
            try:
                from .dispatch_toggle_series_state import DispatchToggleSeriesState
            except ImportError:
                log.exception("DispatchToggleSeriesState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_DS_STATE, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleSeriesState")
                result = DispatchToggleSeriesState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_DATA_TBL_STATE:
            try:
                from .dispatch_toggle_data_tbl_state import DispatchToggleDataTblState
            except ImportError:
                log.exception("DispatchToggleDataTblState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_DATA_TBL_STATE, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleDataTblState")
                result = DispatchToggleDataTblState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CODE_DEL:
            try:
                from .dispatch_del_py_cell import DispatchDelPyCell
            except ImportError:
                log.exception("DispatchDelPyCell import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CODE_DEL, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchDelPyCell")
                result = DispatchDelPyCell(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PY_OBJ_STATE:
            try:
                from .dispatch_py_obj_state import DispatchPyObjState
            except ImportError:
                log.exception("DispatchPyObjState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PY_OBJ_STATE, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyObjState")
                result = DispatchPyObjState(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CELL_SELECT:
            try:
                from .dispatch_cell_select import DispatchCellSelect
            except ImportError:
                log.exception("DispatchCellSelect import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CELL_SELECT, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCellSelect")
                result = DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CELL_SELECT_RECALC:
            try:
                from .dispatch_cell_select_recalc import DispatchCellSelectRecalc
            except ImportError:
                log.exception("DispatchCellSelectRecalc import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CELL_SELECT_RECALC, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCellSelectRecalc")
                result = DispatchCellSelectRecalc(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_DF_CARD:
            try:
                from .dispatch_card_df import DispatchCardDf
            except ImportError:
                log.exception("DispatchCardDf import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_DF_CARD, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCardDf")
                result = DispatchCardDf(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_DATA_TBL_CARD:
            try:
                from .dispatch_card_tbl_data import DispatchCardTblData
            except ImportError:
                log.exception("DispatchCardTblData import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_DATA_TBL_CARD, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCardTblData")
                result = DispatchCardTblData(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_SEL_RNG:
            try:
                from .dispatch_rng_select_popup import DispatchRngSelectPopup
            except ImportError:
                log.exception("DispatchRngSelectPopup import error")
                raise
            try:
                if URL.Arguments:
                    args = self._convert_query_to_dict(URL.Arguments)
                else:
                    args = {}

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_SEL_RNG, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchRngSelectPopup")
                result = DispatchRngSelectPopup(**args)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_ABOUT:
            try:
                from .dispatch_about import DispatchAbout
            except ImportError:
                log.exception("DispatchAbout import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_ABOUT, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchAbout")
                result = DispatchAbout()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_CELL_CTl_UPDATE:
            try:
                from .dispatch_ctl_update import DispatchCtlUpdate
            except ImportError:
                log.exception("DispatchCtlUpdate import error")
                raise

            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_CELL_CTl_UPDATE, doc=self._doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCtlUpdate")
                result = DispatchCtlUpdate(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PIP_PKG_INSTALL:
            try:
                from .dispatch_py_pkg_install import DispatchPyPkgInstall
            except ImportError:
                log.exception("DispatchPyPkgInstall import error")
                raise

            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PIP_PKG_INSTALL, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgInstall")
                result = DispatchPyPkgInstall()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PIP_PKG_UNINSTALL:
            try:
                from .dispatch_py_pkg_uninstall import DispatchPyPkgUninstall
            except ImportError:
                log.exception("DispatchPyPkgUninstall import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PIP_PKG_UNINSTALL, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgUninstall")
                result = DispatchPyPkgUninstall()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PIP_PKG_INSTALLED:
            try:
                from .dispatch_py_pkg_installed import DispatchPyPkgInstalled
            except ImportError:
                log.exception("DispatchPyPkgInstalled import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PIP_PKG_INSTALLED, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgInstalled")
                result = DispatchPyPkgInstalled()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PIP_PKG_LINK:
            try:
                from .dispatch_py_link import DispatchPyLink
            except ImportError:
                log.exception("DispatchPyLink import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PIP_PKG_LINK, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyLink")
                result = DispatchPyLink()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Main == UNO_DISPATCH_PIP_PKG_UNLINK:
            try:
                from .dispatch_py_unlink import DispatchPyUnlink
            except ImportError:
                log.exception("DispatchPyUnlink import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=UNO_DISPATCH_PIP_PKG_UNLINK, doc=self._doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyUnlink")
                result = DispatchPyUnlink()

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        return self._slave.queryDispatch(URL, TargetFrameName, SearchFlags)

    def queryDispatches(self, Requests: Tuple[DispatchDescriptor, ...]) -> Tuple[XDispatch, ...]:
        """
        Actually this method is redundant to XDispatchProvider.queryDispatch() to avoid multiple remote calls.

        It's not allowed to pack it - because every request must match to its real result. Means: don't delete NULL entries inside this list.
        """
        return ()

    def dispose(self) -> None:
        if self._key in DispatchProviderInterceptor._instances:
            del DispatchProviderInterceptor._instances[self._key]

    @classmethod
    def has_instance(cls, doc: OfficeDocumentT) -> bool:
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        doc.runtime_uid
        key = f"dpi_{doc.runtime_uid}"
        return key in cls._instances


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"dpi_{uid}"
    if key in DispatchProviderInterceptor._instances:
        del DispatchProviderInterceptor._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
