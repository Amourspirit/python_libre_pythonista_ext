from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING
import unohelper


if TYPE_CHECKING:
    try:
        # python 3.12+
        from typing import override  # type: ignore
    except ImportError:
        from typing_extensions import override
    from com.sun.star.util import URL
    from com.sun.star.frame import XDispatch
    from com.sun.star.frame import XStatusListener
    from com.sun.star.beans import PropertyValue
else:

    def override(func):  # noqa: ANN001, ANN201
        return func


import unohelper

from com.sun.star.frame import XDispatch


class CalcSheetDispatch(XDispatch, unohelper.Base):
    IMPLE_NAME = "___lo_identifier___.ProtocolHandler.CalcSheetDispatch"
    SERVICE_NAMES = ("com.sun.star.frame.XDispatch",)

    @classmethod
    def get_imple(cls) -> Tuple[Any, str, Tuple[str, ...]]:
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)

    def __init__(self, ctx: Any, frame: Any) -> None:  # noqa: ANN401
        unohelper.Base.__init__(self)
        XDispatch.__init__(self)
        self.ctx = ctx
        self.frame = frame
        # self.toolkit = ctx.getServiceManager().createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)

    @override
    def dispatch(self, URL: URL, Arguments: Tuple[PropertyValue, ...]) -> None:  # noqa: N803
        try:
            if TYPE_CHECKING:
                from pythonpath.libre_pythonista_lib.dispatch.calc_sheet_dispatch_mgr import CalcSheetDispatchMgr
            else:
                from libre_pythonista_lib.dispatch.calc_sheet_dispatch_mgr import CalcSheetDispatchMgr

            mgr = CalcSheetDispatchMgr(self.ctx, self.frame)
            mgr.dispatch(URL, Arguments)

        except Exception as e:
            print(e)
        finally:
            return

    @override
    def addStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        return

    @override
    def removeStatusListener(self, Control: XStatusListener, URL: URL) -> None:  # noqa: N802, N803
        return


# region Implementation

g_ImplementationHelper = unohelper.ImplementationHelper()  # noqa: N816
g_ImplementationHelper.addImplementation(*CalcSheetDispatch.get_imple())

# endregion Implementation
