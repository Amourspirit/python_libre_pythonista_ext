from __future__ import annotations


from typing import TYPE_CHECKING
from ooodev.exceptions import ex as mEx  # noqa: N812


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcSheetView
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryFormDesignMode(QryBase, LogMixin, QryDocT[bool | None]):
    def __init__(self, doc: CalcDoc) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc

    def _get_view(self) -> CalcSheetView | None:
        try:
            view = self._doc.get_view()
            if view.view_controller_name == "Default":
                self.log.debug("View controller is Default.")
                return view
            else:
                # this could mean that the print preview has been activated.
                # Print Preview view controller Name: PrintPreview
                self.log.debug(
                    "'%s' is not the default view controller. Returning None.",
                    view.view_controller_name,
                )
            return None

        except mEx.MissingInterfaceError as e:
            self.log.debug("Error getting view from document. %s", e)
            return None

    def execute(self) -> bool | None:
        """
        Executes the query to check if the document is in form design mode.

        Returns:
            bool | None: True if the document is in form design mode, None if unable to get the view; False otherwise.
        """
        view = self._get_view()
        if view is None:
            self.log.debug("View is None. May be print preview. Returning.")
            return None

        try:
            return view.is_form_design_mode()
        except Exception:
            self.log.exception("Error executing query")
        return None
