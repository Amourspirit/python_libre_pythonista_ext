from __future__ import annotations
from typing import TYPE_CHECKING, Union

from ooodev.io.sfa import Sfa

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName


# I was checking for the existence of folder vnd.sun.star.tdoc:/1/librepythonista.
# However this was not working then when the document was first opened.
# Closing the document and reopening using the sfa folder check was failing while the document was starting up in LoadFinishedJob.
# I also tried checking for the existence of the custom property LP_DOCUMENT for document properties.
# The document properties are read also using sfa and had the same issue.


class QryIsDocPythonista(QryBase, LogMixin, QryDocT[Union[Result[bool, None], Result[None, Exception]]]):
    def __init__(self, doc: CalcDoc) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._sfa = Sfa()
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _qry_cell_cp_code_name(self) -> str:
        """
        Query class that retrieves the codename from configuration.
        Something like ``libre_pythonista_codename``

        Returns:
            str: The codename used for filtering cells.
        """
        qry = QryCellCpCodeName()
        return self._execute_qry(qry)

    def _get_has_cells(self) -> bool:
        """
        Checks if the document has cells with custom properties.

        Returns:
            bool: True if the document has cells with custom properties, False otherwise.
        """
        filter_key = self._qry_cell_cp_code_name()
        for sheet in self._doc.sheets:
            code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)
            if len(code_cell) > 0:
                return True

        return False

    def execute(self) -> Union[Result[bool, None], Result[None, Exception]]:
        """
        Executes the query to check if the document is a LibrePythonista document.

        Returns:
            Result: Success with True if the document is a LibrePythonista document, False otherwise; Failure with Exception.
        """
        try:
            has_cells = self._get_has_cells()
            self.log.debug("is LibrePythonista doc: %s", has_cells)
            return Result.success(has_cells)
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)
