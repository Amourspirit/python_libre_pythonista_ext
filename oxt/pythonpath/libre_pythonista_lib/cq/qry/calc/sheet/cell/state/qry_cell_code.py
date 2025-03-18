from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySrcProvider
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source import PySrcProvider
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.log.log_mixin import LogMixin


# tested in: tests/test_cmd/test_cmd_append_code.py


class QryCellCode(QryBase, LogMixin, QryCellT[str | None]):
    """
    Query to retrieve Python source code associated with a cell.

    Args:
        cell (CalcCell): The cell to query code from
        mod (PyModuleT): The Python module associated with the cell
        src_provider (PySrcProvider | None, optional): Source provider for the code. Defaults to None.
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT, src_provider: PySrcProvider | None = None) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._mod = mod
        self._src_provider = src_provider
        self._py_src_mgr = cast(PySourceManager, None)

    def _get_py_src_mgr(self) -> PySourceManager:
        """
        Gets a PySourceManager instance for the current module.

        Returns:
            PySourceManager: A singleton instance keyed by module
        """
        return PySourceManager(doc=self.cell.calc_doc, mod=self._mod, src_provider=self._src_provider)

    def execute(self) -> str | None:
        """
        Executes the query to retrieve the source code for the cell.

        Returns:
            str | None: The source code if found, None if the cell has no associated code or on error
        """
        try:
            if not isinstance(self._py_src_mgr, PySourceManager):
                self._py_src_mgr = self._get_py_src_mgr()
            if not self.cell.cell_obj in self._py_src_mgr:
                self.log.debug("Cell %s does not exist in source manager.", self.cell.cell_obj)
                return None
            return self._py_src_mgr[self.cell.cell_obj].source_code
        except Exception:
            self.log.exception("Error executing query")
            return None

    @property
    def cell(self) -> CalcCell:
        """
        Get the cell associated with this query.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
