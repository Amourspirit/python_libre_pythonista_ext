from __future__ import annotations
from typing import Tuple
from com.sun.star.awt import XDialog2
from com.sun.star.lang import XTypeProvider
from com.sun.star.awt import XTopWindow2
from com.sun.star.awt import XSystemDependentWindowPeer
from com.sun.star.awt import XVclContainer
from com.sun.star.awt import XVclContainerPeer
from com.sun.star.awt import XWindow2
from com.sun.star.awt import XVclWindowPeer
from com.sun.star.awt import XLayoutConstrains
from com.sun.star.awt import XView
from com.sun.star.awt import XDockableWindow
from com.sun.star.accessibility import XAccessible
from com.sun.star.lang import XEventListener
from com.sun.star.beans import XPropertySetInfo
from com.sun.star.awt import XStyleSettingsSupplier
from com.sun.star.awt import XDevice
from com.sun.star.awt import XUnitConversion
from com.sun.star.uno import XWeak
from com.sun.star.awt import Size


class WindowType(
    XDialog2,
    XTypeProvider,
    XTopWindow2,
    XSystemDependentWindowPeer,
    XVclContainer,
    XVclContainerPeer,
    XWindow2,
    XVclWindowPeer,
    XLayoutConstrains,
    XView,
    XDockableWindow,
    XAccessible,
    XEventListener,
    XPropertySetInfo,
    XStyleSettingsSupplier,
    XDevice,
    XUnitConversion,
    XWeak,
):

    @property
    def Size(self) -> Size: ...

    @property
    def Windows(self) -> Tuple[WindowType, ...]: ...
