from __future__ import annotations

from typing import TYPE_CHECKING, Dict
from ooodev.utils.data_type.cell_obj import CellObj


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.index_cell_props import IndexCellProps
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName


class QryLpCells(QryBase, LogMixin, QryDocT[Dict[int, Dict[CellObj, IndexCellProps]]]):
    """
    Query class that retrieves cells with custom properties in a LibreOffice Calc document.

    This class inherits from QryBase, LogMixin, and QryDocT. It searches through all sheets
    in a Calc document to find cells that have specific custom properties defined.

    Args:
        doc (CalcDoc): The Calc document to query.

    Returns:
        Dict[int, Dict[CellObj, IndexCellProps]]: A dictionary mapping sheet indices to another dictionary
        that maps CellObj instances to their corresponding IndexCellProps.

    Note:
        The return value is sorted by sheet index. Each item ist sorted by CellObj.
    """

    def __init__(self, doc: CalcDoc) -> None:
        """
        Initialize the query with a Calc document.

        Args:
            doc (CalcDoc): The Calc document to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
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

    def _get_cells(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        """
        Retrieves all cells with custom properties in the document.

        Searches through all sheets in the document for cells that have the specific
        custom property defined by the codename from _qry_cell_cp_code_name().

        Returns:
            Dict[int, Dict[CellObj, IndexCellProps]]: A dictionary mapping sheet indices to another dictionary
            that maps CellObj instances to their corresponding IndexCellProps.
        """
        filter_key = self._qry_cell_cp_code_name()
        code_cells: Dict[int, Dict[CellObj, IndexCellProps]] = {}
        sheet_indexes = []
        for sheet in self._doc.sheets:
            sheet_indexes.append(sheet.sheet_index)
        sheet_indexes.sort()

        for idx in sheet_indexes:
            sheet = self._doc.sheets[idx]
            code_index: Dict[CellObj, IndexCellProps] = {}
            index = sheet.sheet_index
            # deleted cells will not be in the custom properties

            code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)  # sorted order
            i = -1
            for key, value in code_cell.items():
                i += 1
                cell = sheet[key]
                code_name = cell.get_custom_property(filter_key, "")
                if not code_name:
                    self.log.error("_get_cells() Code Name not found for cell: %s. Skipping?", cell)
                    continue
                code_index[key] = IndexCellProps(code_name, value, i)
            code_cells[index] = code_index
        return code_cells

    def execute(self) -> Dict[int, Dict[CellObj, IndexCellProps]]:
        """
        Executes the query to retrieve cells with custom properties.

        Returns:
            Dict[int, Dict[CellObj, IndexCellProps]]: A dictionary mapping sheet indices to another dictionary
            that maps CellObj instances to their corresponding IndexCellProps.
        """
        try:
            return self._get_cells()
        except Exception:
            self.log.exception("Error executing query")
        return {}
