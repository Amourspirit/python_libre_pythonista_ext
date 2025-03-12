from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.log.log_mixin import LogMixin

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryCellUri(QryBase, LogMixin, QryCellT[str]):
    """
    Gets the URI for a cell.

    In format of ``vnd.sun.star.tdoc:/1/librepythonista/sheet_unique_id_bla_bla/code_name_bla_bla.py``
    """

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell

    def _get_code_name(self) -> str:
        qry = QryCodeName(cell=self._cell)
        return self._execute_qry(qry)

    def _get_root_uri(self) -> str:
        qry = QryLpRootUri(doc=self._cell.calc_sheet.calc_doc)
        return self._execute_qry(qry)

    def execute(self) -> str:
        """
        Executes the query to get the URI for a cell.

        In format of ``vnd.sun.star.tdoc:/1/librepythonista/sheet_unique_id_bla_bla/code_name_bla_bal.py``

        Returns:
            str: The URI for a cell.
        """

        code_name = self._get_code_name()
        if not code_name:
            self.log.error("Code name not found. Returning empty string.")
            return ""

        root_uri = self._get_root_uri()
        if not root_uri:
            self.log.error("Root URI not found. Returning empty string.")
            return ""

        uri = f"{root_uri}/{self._cell.calc_sheet.unique_id}/{code_name}.py"
        return uri

    @property
    def cell(self) -> CalcCell:
        return self._cell
