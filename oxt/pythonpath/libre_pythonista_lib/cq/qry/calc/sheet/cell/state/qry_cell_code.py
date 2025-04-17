from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from libre_pythonista_lib.cq.qry.calc.doc.qry_py_module_default import QryPyModuleDefault
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result


# tested in: tests/test_cmd/test_cmd_append_code.py


class QryCellCode(QryBase, LogMixin, QryCellT[Result[str, None] | Result[None, Exception]]):
    """
    Query to retrieve Python source code associated with a cell.

    Args:
        cell (CalcCell): The cell to query code from
        mod (PyModuleT): The Python module associated with the cell
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT | None = None) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._py_src_mgr = cast(PySourceManager, None)
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_mod(self) -> PyModuleT:
        """
        Gets the Python module via query.

        Returns:
            PyModuleT: The default Python module for the document
        """
        qry = QryPyModuleDefault()
        return self._execute_qry(qry)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Gets a PySourceManager instance for the current module.

        Returns:
            PySourceManager: A singleton instance keyed by module
        """
        qry = QryPySrcMgrCode(doc=self.cell.calc_doc, mod=self._mod)
        return self._execute_qry(qry)

    def execute(self) -> Result[str, None] | Result[None, Exception]:
        """
        Executes the query to retrieve the source code for the cell.

        Returns:
            str | None: The source code if found, None if the cell has no associated code or on error
        """
        try:
            if self._mod is None:
                self._mod = self._qry_mod()
            if not isinstance(self._py_src_mgr, PySourceManager):
                self._py_src_mgr = self._qry_py_src_mgr()
            if not self.cell.cell_obj in self._py_src_mgr:
                self.log.debug("Cell %s does not exist in source manager.", self.cell.cell_obj)
                return Result.failure(Exception("Cell does not exist in source manager"))
            return Result.success(self._py_src_mgr[self.cell.cell_obj].source_code)
        except Exception as e:
            self.log.exception("Error executing query")
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this query.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
