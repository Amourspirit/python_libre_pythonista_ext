from __future__ import annotations
from typing import TYPE_CHECKING, cast, Any
from .dialog_base import DialogBase

from ..oxt_logger import OxtLogger

if TYPE_CHECKING:
    from com.sun.star.ui.dialogs import FilePicker  # service
    from com.sun.star.util import PathSubstitution  # service


class FileOpenDialog(DialogBase):
    """To get file url to open."""

    def __init__(self, ctx, **kwargs):
        """
        Constructor

        Args:
            ctx (Any): Component context

        Keyword Args:
            template (str): Template url.
            title (str): Title of the dialog.
            default (str): Default file name.
            directory (str): Initial directory.
            filters (list): List of filters.
        """
        super().__init__(ctx)
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("FileOpenDialog.__init__")
        self.args = kwargs
        try:
            AvailableServiceNames = self.ctx.getServiceManager().getAvailableServiceNames()
            if "com.sun.star.ui.dialogs.SystemFilePicker" in AvailableServiceNames:
                self.file_picker_service = "com.sun.star.ui.dialogs.SystemFilePicker"
            elif "com.sun.star.ui.dialogs.GtkFilePicker" in AvailableServiceNames:
                self.file_picker_service = "com.sun.star.ui.dialogs.GtkFilePicker"
            else:
                self.file_picker_service = "com.sun.star.ui.dialogs.FilePicker"
        except Exception as err:
            self._logger.error(f"FileOpenDialog.__init__: {err}", exc_info=True)
            raise
        self._logger.debug("FileOpenDialog.__init__ done")

    def execute(self) -> str:
        """
        Execute the dialog.

        Returns:
            str: Path if selected, else empty string.
        """
        # sourcery skip: extract-method
        self._logger.debug("FileOpenDialog.execute")
        fp = cast("FilePicker", self.create(self.file_picker_service))
        try:
            if "template" in self.args:
                fp.initialize((self.args["template"],))  # type: ignore
            if "title" in self.args:
                fp.setTitle(self.args["title"])
            if "default" in self.args:
                default = self.args["default"]
                fp.setDefaultName(self._substitute_variables(default))
            if "directory" in self.args:
                fp.setDisplayDirectory(self.args["directory"])
            args = self.args
            if "filters" in self.args:
                for title, filter in self.args["filters"]:
                    fp.appendFilter(title, filter)
            return fp.getFiles()[0] if fp.execute() else ""
        except Exception as err:
            self._logger.error(f"FileOpenDialog.execute: {err}", exc_info=True)
            raise

    def _substitute_variables(self, uri):
        path_sub = cast("PathSubstitution", self.create("com.sun.star.util.PathSubstitution"))
        return path_sub.substituteVariables(uri, True)
