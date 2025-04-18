from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING
from urllib.parse import parse_qs

from com.sun.star.util import URL

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const import (
    PATH_CELL_CTl_UPDATE,
    PATH_CELL_SELECT_RECALC,
    PATH_CELL_SELECT,
    PATH_CODE_DEL,
    PATH_CODE_EDIT_MB,
    PATH_DATA_TBL_CARD,
    PATH_DATA_TBL_STATE,
    PATH_DF_CARD,
    PATH_DF_STATE,
    PATH_DS_STATE,
    PATH_PY_OBJ_STATE,
    PATH_SEL_RNG,
)

from ..const.event_const import LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
from ..log.log_inst import LogInst
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from oxt.___lo_pip___.config import Config
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.general.qry_ctx_runtime_uid import QryCtxRuntimeUID
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from ___lo_pip___.config import Config
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.general.qry_ctx_runtime_uid import QryCtxRuntimeUID
    from libre_pythonista_lib.utils.result import Result


class CalcSheetDispatchMgr:
    def __init__(self, ctx: Any, frame: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self.frame = frame
        self._config = Config()
        self._runtime_id = None

    def _convert_query_to_dict(self, query: str) -> Dict[str, str]:
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:  # type: ignore # noqa: N802, N803
        log = LogInst()
        se = SharedEvent()
        doc = Lo.current_doc

        if URL.Path == PATH_CODE_EDIT_MB:
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
                    from .dispatch_edit_py_cell_mb2 import (
                        DispatchEditPyCellMb2 as DispatchEditPyCell,
                    )
                except ImportError:
                    log.exception("DispatchEditPyCellMb2 import error")
                    raise

            try:
                args = self._convert_query_to_dict(URL.Arguments)
                in_thread = args.pop("in_thread", "0") == "1"
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(
                    url=URL,
                    cmd=URL.Complete,
                    doc=doc,
                    in_thread=in_thread,
                    experiential_edit=is_experiential,
                    **args,
                )

                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    if is_experiential:
                        log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchEditPyCellWv")
                    else:
                        log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchEditPyCellMb2")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_CELL_SELECT:
            try:
                from .dispatch_cell_select import DispatchCellSelect
            except ImportError:
                log.exception("DispatchCellSelect import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchCellSelect")
                result = DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_CODE_DEL:
            try:
                from .dispatch_del_py_cell2 import DispatchDelPyCell2
            except ImportError:
                log.exception("DispatchDelPyCell2 import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchDelPyCell2")
                result = DispatchDelPyCell2(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_CELL_SELECT_RECALC:
            try:
                from .dispatch_cell_select_recalc import DispatchCellSelectRecalc
            except ImportError:
                log.exception("DispatchCellSelectRecalc import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchCellSelectRecalc")
                result = DispatchCellSelectRecalc(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception(f"Dispatch Error: {URL.Main}")
                return None

        elif URL.Path == PATH_DF_STATE:
            try:
                from .dispatch_toggle_df_state2 import DispatchToggleDfState2
            except ImportError:
                log.exception("DispatchToggleDfState2 import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchToggleDfState2")
                result = DispatchToggleDfState2(sheet=args["sheet"], cell=args["cell"], uid=self.runtime_uid)
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)

                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_DF_CARD:
            try:
                from .dispatch_card_df import DispatchCardDf
            except ImportError:
                log.exception("DispatchCardDf import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchCardDf")
                result = DispatchCardDf(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_DATA_TBL_CARD:
            try:
                from .dispatch_card_tbl_data import DispatchCardTblData
            except ImportError:
                log.exception("DispatchCardTblData import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchCardTblData")
                result = DispatchCardTblData(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_CELL_CTl_UPDATE:
            try:
                from .dispatch_ctl_update2 import DispatchCtlUpdate2
            except ImportError:
                log.exception("DispatchCtlUpdate2 import error")
                raise

            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchCtlUpdate2")
                result = DispatchCtlUpdate2(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_SEL_RNG:
            try:
                from .dispatch_rng_select_popup import DispatchRngSelectPopup
            except ImportError:
                log.exception("DispatchRngSelectPopup import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments) if URL.Arguments else {}

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchRngSelectPopup")
                result = DispatchRngSelectPopup(**args)
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_DS_STATE:
            try:
                from .dispatch_toggle_series_state import DispatchToggleSeriesState
            except ImportError:
                log.exception("DispatchToggleSeriesState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchToggleSeriesState")
                result = DispatchToggleSeriesState(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_DATA_TBL_STATE:
            try:
                from .dispatch_toggle_data_tbl_state2 import DispatchToggleDataTblState2
            except ImportError:
                log.exception("DispatchToggleDataTblState2 import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchToggleDataTblState2")
                result = DispatchToggleDataTblState2(sheet=args["sheet"], cell=args["cell"], uid=self.runtime_uid)
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PY_OBJ_STATE:
            try:
                from .dispatch_py_obj_state import DispatchPyObjState
            except ImportError:
                log.exception("DispatchPyObjState import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchPyObjState")
                result = DispatchPyObjState(sheet=args["sheet"], cell=args["cell"])
                result.dispatch(URL, Arguments)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return None
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        return None

    @property
    def runtime_uid(self) -> str:
        if self._runtime_id is None:
            qry_handler = QryHandlerFactory.get_qry_handler()
            qry = QryCtxRuntimeUID(ctx=self.ctx)
            qry_result = qry_handler.handle(qry)
            self._runtime_id = qry_result.data if Result.is_success(qry_result) else ""
        return self._runtime_id
