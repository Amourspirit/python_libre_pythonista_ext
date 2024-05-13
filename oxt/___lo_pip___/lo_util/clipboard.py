from __future__ import annotations
from typing import Any, Tuple, TYPE_CHECKING, cast
import uno
import unohelper
from com.sun.star.datatransfer import XTransferable
from com.sun.star.datatransfer import DataFlavor  # struct
from com.sun.star.datatransfer.clipboard import XClipboardOwner
from com.sun.star.datatransfer.clipboard import XClipboard

from .util import Util


# https://wiki.openoffice.org/wiki/Documentation/DevGuide/OfficeDev/Common_Application_Features


class Transferable(unohelper.Base, XTransferable):
    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def getTransferData(self, flavor: DataFlavor) -> Any:
        """
        Called by a data consumer to obtain data from the source in a specified format.

        Raises:
            UnsupportedFlavorException: ``UnsupportedFlavorException``
            com.sun.star.io.IOException: ``IOException``
        """
        return self._text if flavor.MimeType == "text/plain;charset=utf-16" else None

    def getTransferDataFlavors(self) -> Tuple[DataFlavor, ...]:
        """
        Returns a sequence of supported DataFlavor.
        """
        flavor = DataFlavor()
        flavor.MimeType = "text/plain;charset=utf-16"
        flavor.HumanPresentableName = "Unicode-Text"
        return (flavor,)

    def isDataFlavorSupported(self, flavor: DataFlavor) -> bool:
        """
        Checks if the data object supports the specified data flavor.

        A value of FALSE if the DataFlavor is unsupported by the transfer source.
        """
        return flavor.MimeType == "text/plain;charset=utf-16"

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value


class ClipboardOwner(unohelper.Base, XClipboardOwner):
    def __init__(self) -> None:
        super().__init__()
        self._is_owner = True

    def lostOwnership(self, clipboard: Any, contents: Any) -> None:
        """
        Notifies the clipboard owner that it has lost ownership of the clipboard to another object.

        Parameters:
            clipboard: The clipboard that is no longer owned.
            contents: The contents which this owner had placed on the clipboard.
        """
        self._is_owner = False

    @property
    def is_owner(self) -> bool:
        return self._is_owner


def copy_to_clipboard(text: str) -> None:
    """Copies text to system clipboard.

    Args:
        text (str): Text to copy.
    """
    util = Util()
    clip = cast(XClipboard, util.create_uno_service("com.sun.star.datatransfer.clipboard.SystemClipboard"))
    owner = ClipboardOwner()
    transferable = Transferable(text)
    transferable.text = text
    clip.setContents(transferable, owner)
