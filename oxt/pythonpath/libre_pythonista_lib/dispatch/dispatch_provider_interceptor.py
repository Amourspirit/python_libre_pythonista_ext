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

# from ooodev.calc import CalcDoc

from ..const.event_const import GBL_DOC_CLOSING

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from ....___lo_pip___.config import Config
else:
    from ___lo_pip___.config import Config

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

    def __new__(cls, doc: OfficeDocumentT, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        # sc = Lo.xscript_context
        # doc = sc.getDocument()
        # uid = doc.RuntimeUID

        uid = doc.runtime_uid
        key = f"dpi_{uid}"
        if key not in cls._instances:
            inst = super(DispatchProviderInterceptor, cls).__new__(cls, *args, **kwargs)
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

        # log = LogInst()
        # log.debug("DispatchProviderInterceptor.queryDispatch: %s", URL.Complete)

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
        if self._key in DispatchProviderInterceptor._instances:
            del DispatchProviderInterceptor._instances[self._key]

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
    if key in DispatchProviderInterceptor._instances:
        del DispatchProviderInterceptor._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
