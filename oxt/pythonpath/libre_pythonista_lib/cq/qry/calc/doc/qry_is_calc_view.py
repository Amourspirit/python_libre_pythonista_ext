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


class QryIsCalcView(QryBase, LogMixin, QryDocT[bool]):
    """Query that checks if the current view is a Calc (spreadsheet) view in Default mode."""

    def __init__(self, doc: CalcDoc) -> None:
        """
        Initialize the query.

        Args:
            doc (CalcDoc): The Calc document to check.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _get_view(self) -> CalcSheetView:
        """
        Get the current view and verify it's in Default mode.

        Returns:
            CalcSheetView: The current sheet view.

        Raises:
            NotSupportedError: If view controller is not in Default mode.
        """
        view = self._doc.get_view()
        if view.view_controller_name == "Default":
            self.log.debug("View controller is Default.")
            return view
        raise mEx.NotSupportedError("View controller is not Default.")

    def execute(self) -> bool:
        """
        Execute the query to check if current view is a valid Calc view.

        Returns:
            bool: True if view is a valid Calc view in Default mode, False otherwise.
        """
        try:
            _ = self._get_view()
            self.log.debug("is Calc view: True")
            return True
        except mEx.NotSupportedError as e:
            self.log.debug("%s", e)
        except mEx.MissingInterfaceError as e:
            self.log.debug("Not a Spreadsheet view: %s", e)
        except Exception:
            self.log.exception("Error executing query")
        self.log.debug("is Calc view: False")
        return False
