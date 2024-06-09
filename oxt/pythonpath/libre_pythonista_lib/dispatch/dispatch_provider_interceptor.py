from __future__ import annotations
from typing import Tuple
from urllib.parse import parse_qs
import contextlib
import uno
import unohelper
from com.sun.star.frame import XDispatchProviderInterceptor
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.util import URL
from com.sun.star.frame import DispatchDescriptor

from ooodev.loader import Lo
from ooodev.calc import CalcDoc

# from ooodev.calc import CalcDoc
from .dispatch_edit_py import DispatchEditPY


class DispatchProviderInterceptor(unohelper.Base, XDispatchProviderInterceptor):
    """
    Dispatch Provider Interceptor.

    This class needs to be kept alive as long as the dispatch provider is in use.
    For this reason this class is a singleton.

    Calling the ``dispose()`` method will release the singleton instance.
    """

    _instances = {}

    def __new__(cls, doc: CalcDoc, *args, **kwargs):
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

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_initialized", False):
            return
        self._master = None
        self._slave = None
        self._initialized = True
        self._key: str

    # def _convert_query_to_dict(self, query: str):
    #     return parse_qs(query)

    def _convert_query_to_dict(self, query: str):
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

    def getMasterDispatchProvider(self) -> XDispatchProvider:
        """
        access to the master XDispatchProvider of this interceptor
        """
        return self._master

    def getSlaveDispatchProvider(self) -> XDispatchProvider:
        """
        access to the slave XDispatchProvider of this interceptor
        """
        return self._slave

    def setMasterDispatchProvider(self, new_supplier: XDispatchProvider) -> None:
        """
        sets the master XDispatchProvider, which may forward calls to its XDispatchProvider.queryDispatch() to this dispatch provider.
        """
        self._master = new_supplier

    def setSlaveDispatchProvider(self, new_dispatch_provider: XDispatchProvider) -> None:
        """
        sets the slave XDispatchProvider to which calls to XDispatchProvider.queryDispatch() can be forwarded under control of this dispatch provider.
        """
        self._slave = new_dispatch_provider

    def queryDispatch(self, url: URL, target_frame_name: str, search_flags: int) -> XDispatch | None:
        """
        Searches for an XDispatch for the specified URL within the specified target frame.
        """
        if url.Protocol == "slot:":
            # not really sure if this is necessary but there have been reports in the past
            # of crashes without this check.
            return None

        if url.Main == ".uno:libre_pythonista.calc.menu.code.edit":
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                return DispatchEditPY(sheet=args["sheet"], cell=args["cell"])
        # elif url.Main == ".uno:libre_pythonista.calc.menu.update.orig":
        #     with contextlib.suppress(Exception):
        #         args = self._convert_query_to_dict(url.Arguments)
        #         return DispatchUpdateOriginalValue(sheet=args["sheet"], cell=args["cell"])
        return self._slave.queryDispatch(url, target_frame_name, search_flags)

    def queryDispatches(self, requests: Tuple[DispatchDescriptor, ...]) -> Tuple[XDispatch, ...]:
        """
        Actually this method is redundant to XDispatchProvider.queryDispatch() to avoid multiple remote calls.

        It's not allowed to pack it - because every request must match to its real result. Means: don't delete NULL entries inside this list.
        """
        pass

    def dispose(self) -> None:
        if self._key in DispatchProviderInterceptor._instances:
            del DispatchProviderInterceptor._instances[self._key]

    @classmethod
    def has_instance(cls, doc: CalcDoc) -> bool:
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        doc.runtime_uid
        key = f"dpi_{doc.runtime_uid}"
        return key in cls._instances
