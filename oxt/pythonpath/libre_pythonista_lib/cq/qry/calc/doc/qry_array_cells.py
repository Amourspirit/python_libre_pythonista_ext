from __future__ import annotations
from typing import List, TYPE_CHECKING

from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcDoc, CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_array_ability import QryArrayAbility
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_pyc_rule import QryPycRule
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


class QryArrayCells(QryBase, LogMixin, QryDocT[Result[List[CalcCell], None] | Result[None, Exception]]):
    """
    Query to get all cells in a document that contain array formulas.
    """

    def __init__(self, doc: CalcDoc) -> None:
        """
        Initialize the query.

        Args:
            doc (CalcDoc): The document to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self.log.debug("init done for doc %s", doc.runtime_uid)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Get the Python source manager for the document.

        Returns:
            PySourceManager: The Python source manager.
        """
        qry = QryPySrcMgrCode(doc=self._doc)
        return self._execute_qry(qry)

    def _has_array_ability(self, cell: CalcCell) -> bool:
        """
        Check if a cell has array formula capability.

        Args:
            cell (CalcCell): The cell to check.

        Returns:
            bool: True if the cell has array formula capability, False otherwise.
        """
        try:
            qry = QryArrayAbility(cell=cell)
            result = self._execute_qry(qry)
            if Result.is_success(result):
                self.log.debug("_has_array_ability() - %s", result.data)
                return result.data
            raise result.error
        except Exception as e:
            self.log.exception("_has_array_ability() error: %s", e)
        return False

    def get_array_cells(self) -> List[CalcCell]:
        """
        Gets all cells in the sheet that have array formulas and are currently displayed as an array formula.

        Returns:
            List[CalcCell]: A list of CalcCell objects that have array formulas.
        """
        results: List[CalcCell] = []
        try:
            cells: List[CellObj] = []
            py_src_mgr = self._qry_py_src_mgr()
            for py_src_data in py_src_mgr.py_src_date_items():
                cells.append(py_src_data.cell)

            cells.sort()

            for cell_obj in cells:
                sheet = self._doc.sheets[cell_obj.sheet_idx]
                calc_cell = sheet[cell_obj]
                if not self._has_array_ability(calc_cell):
                    continue
                results.append(sheet[cell_obj])

            if self.log.is_debug:
                self.log.debug("get_array_cells() - %i", len(results))
        except Exception as e:
            self.log.exception("get_array_cells() getting array cells: %s", e)
            raise e
        return results

    def execute(self) -> Result[List[CalcCell], None] | Result[None, Exception]:
        """
        Execute the query to get array cells.

        Returns:
            Result: Success with list of CalcCells or Failure with Exception
        """
        try:
            result = self.get_array_cells()
            return Result.success(result)
        except Exception as e:
            return Result.failure(e)
