from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin


class QryIsCellInSrc(QryBase, LogMixin, QryCellT[bool]):
    """
    Query to check if a cell is in the source code manager for a given Python module.

    Args:
        cell (CalcCell): The cell to check
        mod (PyModuleT): The Python module to check against
    """

    def __init__(self, cell: CalcCell, mod: PyModuleT) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._mod = mod
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Gets a PySourceManager instance for the current module.

        Returns:
            PySourceManager: A singleton instance keyed by module
        """
        qry = QryPySrcMgrCode(cell=self.cell, mod=self._mod)
        return self._execute_qry(qry)

    def execute(self) -> bool:
        """
        Executes the query to check if the cell exists in the source manager.

        Returns:
            bool: True if the cell exists in the source manager, False otherwise
        """
        mgr = self._qry_py_src_mgr()
        return self.cell.cell_obj in mgr

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell being queried.

        Returns:
            CalcCell: The cell instance
        """
        return self._cell
