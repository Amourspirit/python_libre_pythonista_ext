from __future__ import annotations
from typing import Any, Dict, Union
from urllib.parse import parse_qs
from com.sun.star.frame import XDispatch
from com.sun.star.util import URL

from ooodev.loader import Lo
from ooodev.events.args.event_args import EventArgs
from ooodev.events.args.cancel_event_args import CancelEventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ..const import (
    PATH_ABOUT,
    PATH_LOG_WIN,
    PATH_PIP_PKG_INSTALL,
    PATH_PIP_PKG_UNINSTALL,
    PATH_PIP_PKG_INSTALLED,
    PATH_PIP_PKG_LINK,
    PATH_PIP_PKG_UNLINK,
    PATH_PYC_FORMULA,
    PATH_PYC_FORMULA_DEP,
    PATH_DUMP_SRC_LOG,
)

from ..const.event_const import LP_DISPATCHED_CMD, LP_DISPATCHING_CMD
from ..log.log_inst import LogInst
from ..event.shared_event import SharedEvent


class MainHandlerMgr:
    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        self.ctx = ctx
        self.frame = None
        # self._config = Config()
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

    def query_dispatch(self, URL: URL, TargetFrameName: str, SearchFlags: int) -> Union[XDispatch, None]:  # type: ignore # noqa: N802, N803
        log = LogInst()
        se = SharedEvent()
        doc = Lo.current_doc

        # print(f"URL Main: {URL.Main}")
        # print(f"URL Path: {URL.Path}")
        # print(f"URL Protocol: {URL.Protocol}")

        if URL.Path == PATH_ABOUT:
            # URL.Complete = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:libre_pythonista.ext.about"
            # URL.Main = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:libre_pythonista.ext.about"
            # URL.Protocol = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:"
            # URL.Path = "libre_pythonista.ext.about"
            # URL.Arguments = ""
            try:
                from .dispatch_about import DispatchAbout
            except ImportError:
                log.exception("DispatchAbout import error")
                raise

            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_ABOUT, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchAbout")
                result = DispatchAbout(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_LOG_WIN:
            # URL.Complete = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:libre_pythonista.calc.log_window?in_thread=1"
            # URL.Main = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:libre_pythonista.calc.log_window?in_thread=1"
            # URL.Protocol = "com.github.amourspirit.extensions.librepythonista.ProtocolHandler.ista:"
            # URL.Path = "libre_pythonista.calc.log_window?in_thread=1"
            # URL.Arguments = ""
            try:
                from .dispatch_log_window import DispatchLogWindow
            except ImportError:
                log.exception("DispatchLogWindow import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)
                in_thread = False  # args.pop("in_thread", "0") == "1"

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_LOG_WIN, doc=doc, in_thread=in_thread, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchLogWindow")
                result = DispatchLogWindow(ctx=self.ctx, in_thread=in_thread)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PYC_FORMULA_DEP:
            try:
                from .dispatch_pyc_formula_dep import DispatchPycFormulaDep
            except ImportError:
                log.exception("DispatchPycFormulaDep import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PYC_FORMULA_DEP, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPycFormulaDep")

                result = DispatchPycFormulaDep(ctx=self.ctx)
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PYC_FORMULA:
            try:
                from .dispatch_pyc_formula import DispatchPycFormula
            except ImportError:
                log.exception("DispatchPycFormula import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PYC_FORMULA, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPycFormula")

                result = DispatchPycFormula(ctx=self.ctx)
                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PIP_PKG_INSTALLED:
            try:
                from .dispatch_py_pkg_installed import DispatchPyPkgInstalled
            except ImportError:
                log.exception("DispatchPyPkgInstalled import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PIP_PKG_INSTALLED, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgInstalled")
                result = DispatchPyPkgInstalled(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PIP_PKG_INSTALL:
            try:
                from .dispatch_py_pkg_install import DispatchPyPkgInstall
            except ImportError:
                log.exception("DispatchPyPkgInstall import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PIP_PKG_INSTALL, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgInstall")
                result = DispatchPyPkgInstall(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PIP_PKG_UNINSTALL:
            try:
                from .dispatch_py_pkg_uninstall import DispatchPyPkgUninstall
            except ImportError:
                log.exception("DispatchPyPkgUninstall import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PIP_PKG_UNINSTALL, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyPkgUninstall")
                result = DispatchPyPkgUninstall(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PIP_PKG_LINK:
            try:
                from .dispatch_py_link import DispatchPyLink
            except ImportError:
                log.exception("DispatchPyLink import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PIP_PKG_LINK, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyLink")
                result = DispatchPyLink(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_PIP_PKG_UNLINK:
            try:
                from .dispatch_py_unlink import DispatchPyUnlink
            except ImportError:
                log.exception("DispatchPyUnlink import error")
                raise
            try:
                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(cmd=PATH_PIP_PKG_UNLINK, doc=doc)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                with log.indent(True):
                    log.debug("DispatchProviderInterceptor.queryDispatch: returning DispatchPyUnlink")
                result = DispatchPyUnlink(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        elif URL.Path == PATH_DUMP_SRC_LOG:
            try:
                from .dispatch_dump_src_log import DispatchDumpSrcLog
            except ImportError:
                log.exception("DispatchDumpSrcLog import error")
                raise
            try:
                args = self._convert_query_to_dict(URL.Arguments)

                cargs = CancelEventArgs(self)
                cargs.event_data = DotDict(url=URL, cmd=URL.Complete, doc=doc, **args)
                se.trigger_event(LP_DISPATCHING_CMD, cargs)
                if cargs.cancel is True and cargs.handled is False:
                    return None

                log.debug("CalcSheetDispatchMgr.dispatch: dispatching DispatchDumpSrcLog")
                result = DispatchDumpSrcLog(ctx=self.ctx)

                eargs = EventArgs.from_args(cargs)
                eargs.event_data.dispatch = result
                se.trigger_event(LP_DISPATCHED_CMD, eargs)
                return result
            except Exception:
                log.exception("Dispatch Error: %s", URL.Main)
                return None

        return None
