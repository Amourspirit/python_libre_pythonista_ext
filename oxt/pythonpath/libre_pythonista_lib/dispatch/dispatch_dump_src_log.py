from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING

import unohelper
from com.sun.star.frame import XDispatch
from com.sun.star.beans import PropertyValue
from com.sun.star.util import URL
from ooo.dyn.frame.feature_state_event import FeatureStateEvent
from ooodev.calc import CalcDoc

if TYPE_CHECKING:
    from com.sun.star.frame import XStatusListener
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.log.py_logger import PyLogger
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.log.py_logger import PyLogger
    from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_src_mgr import QryPySrcMgr
    from libre_pythonista_lib.log.log_mixin import LogMixin


class DispatchDumpSrcLog(XDispatch, LogMixin, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.dispatch.DispatchDumpSrcLogWindow"
    SERVICE_NAMES = ("com.sun.star.frame.XDispatch",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XDispatch.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self._status_listeners: Dict[str, XStatusListener] = {}

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        registers a listener of a control for a specific URL at this object to receive status events.

        It is only allowed to register URLs for which this XDispatch was explicitly queried. Additional arguments (\"#...\" or \"?...\") will be ignored.

        Note: Notifications can't be guaranteed! This will be a part of interface XNotifyingDispatch.
        """
        if URL.Complete in self._status_listeners:
            pass
        else:
            # setting IsEnable=False here does not disable the dispatch command
            # State=True may cause the menu items to be displayed as checked.
            fe = FeatureStateEvent(FeatureURL=URL, IsEnabled=True, State=None)
            Control.statusChanged(fe)
            self._status_listeners[URL.Complete] = Control

    @override
    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:  # noqa: N803
        """
        Dispatches (executes) a URL
        """
        try:
            doc = CalcDoc.from_current_doc()
            qry_handler = QryHandlerFactory.get_qry_handler()
            cmd_handler = CmdHandlerFactory.get_cmd_handler()
            qry_src_mgr = QryPySrcMgr(doc=doc)
            py_src = qry_handler.handle(qry_src_mgr)
            src = py_src.dump_module_source_code_to_log()
            PyLogger(doc).info(f" Source Code \n# Start Dump\n{src}\n# End Dump\n")
        except Exception as e:
            self.log.exception("Error: %s", e)
        finally:
            return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        """
        Un-registers a listener from a control.
        """
        if URL.Complete in self._status_listeners:
            del self._status_listeners[URL.Complete]


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*DispatchDumpSrcLog.get_imple())

# endregion Implementation
