from __future__ import annotations
from typing import TYPE_CHECKING, cast, Any
from .dialog_base import DialogBase

from ..oxt_logger import OxtLogger

if TYPE_CHECKING:
    from com.sun.star.ui.dialogs import FolderPicker  # service


class FolderOpenDialog(DialogBase):
    """To get file url to open."""

    def __init__(self, ctx: Any, **kwargs):
        """
        Constructor

        Args:
            ctx (Any): Current Context

        Keyword Args:
            title (str): Title of the dialog.
            directory (str): Initial directory.
            description (str): Description of the dialog.
        """
        super().__init__(ctx)
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("FolderOpenDialog.__init__")
        self.args = kwargs
        try:
            AvailableServiceNames = self.ctx.getServiceManager().getAvailableServiceNames()
            if "com.sun.star.ui.dialogs.SystemFolderPicker" in AvailableServiceNames:
                self.folder_picker_service = "com.sun.star.ui.dialogs.SystemFolderPicker"
            elif "com.sun.star.ui.dialogs.GtkFolderPicker" in AvailableServiceNames:
                self.folder_picker_service = "com.sun.star.ui.dialogs.GtkFolderPicker"
            else:
                self.folder_picker_service = "com.sun.star.ui.dialogs.FolderPicker"
        except Exception as err:
            self._logger.error(f"FolderOpenDialog.__init__: {err}", exc_info=True)
            raise
        self._logger.debug("FolderOpenDialog.__init__ done")

    def execute(self) -> str:
        """
        Execute the dialog.

        Returns:
            str: Path if selected, else empty string.
        """
        # sourcery skip: extract-method
        self._logger.debug("FolderOpenDialog.execute")
        fp = cast("FolderPicker", self.create(self.folder_picker_service))
        try:
            if "title" in self.args:
                fp.setTitle(self.args["title"])
            if "directory" in self.args:
                fp.setDisplayDirectory(self.args["directory"])
            if "description" in self.args:
                fp.setDescription(self.args["description"])
            return fp.getDirectory() if fp.execute() else ""
        except Exception as err:
            self._logger.error(f"FolderOpenDialog.execute: {err}", exc_info=True)
            raise
