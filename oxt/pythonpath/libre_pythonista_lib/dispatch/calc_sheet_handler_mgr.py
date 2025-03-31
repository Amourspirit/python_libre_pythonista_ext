from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING
from urllib.parse import parse_qs

from com.sun.star.frame import XDispatch
from com.sun.star.util import URL

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const import (
    PATH_CODE_EDIT,
    PATH_CODE_EDIT_MB,
    PATH_CODE_DEL,
    PATH_CELL_SELECT,
)

from ..const.event_const import LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
from ..log.log_inst import LogInst
from ..event.shared_event import SharedEvent

if TYPE_CHECKING:
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config


class CalcSheetHandlerMgr:
    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self.frame = None
        self._config = Config()
        # try:
        #     service_mgr = self.ctx.getServiceManager()
        #     desktop = service_mgr.DefaultContext.getByName("/singletons/com.sun.star.frame.theDesktop")
        #     print(desktop)
        #     print(Lo.current_doc)
        # except:
        #     print("Error getting desktop")

    def _convert_query_to_dict(self, query: str) -> Dict[str, str]:
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

    def query_dispatch(self, URL: URL, TargetFrameName: str, SearchFlags: int) -> XDispatch | None:  # type: ignore # noqa: N802, N803
        log = LogInst()
        se = SharedEvent()
        doc = Lo.current_doc

        if URL.Path == PATH_CODE_EDIT:
            try:
                from .dispatch_edit_py_cell import DispatchEditPyCell
            except ImportError:
                log.exception("DispatchEditPyCell import error")
                raise

            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCell")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

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
                        log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCellWv")
                    else:
                        log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCellMb2")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
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
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchCellSelect")
                result = DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
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
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchDelPyCell2")
                result = DispatchDelPyCell2(sheet=args["sheet"], cell=args["cell"])

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        return None
