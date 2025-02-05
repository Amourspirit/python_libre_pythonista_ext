from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING
import unohelper

from com.sun.star.frame import XDispatchProvider
from com.sun.star.lang import XInitialization

if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
    from com.sun.star.util import URL
    from com.sun.star.frame import XDispatch
    from com.sun.star.frame import DispatchDescriptor
else:

    def override(func):  # noqa: ANN001, ANN201
        return func

# https://github.com/marklh9/ExtendingLibreOffice/blob/71a15e72bd9975c282b2d4e858ad933f44d0c3ee/src/ProtocolHandler/handler.py


class MainHandler(XDispatchProvider, XInitialization, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.ProtocolHandler.MainHandler"
    SERVICE_NAMES = ("com.sun.star.frame.ProtocolHandler",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any) -> None:  # noqa: ANN401
        XDispatchProvider.__init__(self)
        XInitialization.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.frame = None
        self.toolkit = ctx.getServiceManager().createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)

    @override
    def initialize(self, aArguments: Tuple[Any, ...]) -> None:  # noqa: N803
        if len(aArguments) > 0:
            self.frame = aArguments[0]

    @override
    def queryDispatch(self, URL: URL, TargetFrameName: str, SearchFlags: int) -> XDispatch | None:  # type: ignore # noqa: N802, N803
        # print(f"MainHandler URL: {URL.Complete}")
        if URL.Protocol == "___lo_identifier___.ProtocolHandler.ista:":
            # service_mgr = self.ctx.getServiceManager()
            # dispatch = service_mgr.createInstanceWithArgumentsAndContext(
            #     "___lo_identifier___.ProtocolHandler.MainHandler", (self.frame,), self.ctx
            # )
            # return dispatch
            if TYPE_CHECKING:
                from ....pythonpath.libre_pythonista_lib.dispatch.main_handler_mgr import MainHandlerMgr
            else:
                from libre_pythonista_lib.dispatch.main_handler_mgr import MainHandlerMgr
            handler = MainHandlerMgr(self.ctx)
            return handler.query_dispatch(URL, TargetFrameName, SearchFlags)
        return None

    @override
    def queryDispatches(self, Requests: Tuple[DispatchDescriptor, ...]) -> Tuple[XDispatch, ...]:  # noqa: N802, N803
        result = []
        for item in Requests:
            result.append(self.queryDispatch(item.FeatureURL, item.FrameName, item.SearchFlags))
        return tuple(result)


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*MainHandler.get_imple())

# endregion Implementation
