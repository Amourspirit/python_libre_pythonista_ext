from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union

from ooodev.calc import CalcCell
from ooodev.utils.data_type.cell_obj import CellObj

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_t import PyModuleT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_source_manager import PySourceManager
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.doc.qry_lp_root_uri import QryLpRootUri
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.state.qry_py_src_mgr import QryPySrcMgrCode

    PySourceManager = Any


class QryCellNext(QryBase, LogMixin, QryCellT[Union[Result[CellObj, None], Result[None, Exception]]]):
    def __init__(self, cell: CalcCell, require_exist: bool = False, mod: Union[PyModuleT, None] = None) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
            require_exist (bool, optional): If True, the cell must exist in the source manager. Defaults to False.
            mod: (PyModuleT, optional) Optional Python module. If not provided, will be queried when needed
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._require_exist = require_exist
        self._mod = mod
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _qry_py_src_mgr(self) -> PySourceManager:
        """
        Gets a PySourceManager instance for the current module.

        Returns:
            PySourceManager: A singleton instance keyed by module
        """
        qry = QryPySrcMgrCode(doc=self.cell.calc_doc, mod=self._mod)
        return self._execute_qry(qry)

    def execute(self) -> Union[Result[CellObj, None], Result[None, Exception]]:
        """
        Executes the query to get the URI for a cell.

        In format of ``vnd.sun.star.tdoc:/1/librepythonista/sheet_unique_id_bla_bla/code_name_bla_bal.py``

        Returns:
            Result: Success with URI or Failure with Exception
        """
        try:
            py_src_mgr = self._qry_py_src_mgr()
            next_cell = py_src_mgr.get_next_item_py_src_data(
                cell=self.cell.cell_obj, require_exist=self._require_exist
            )
            if next_cell is None:
                return Result.failure(Exception("No next cell found"))
            return Result.success(next_cell.cell)
        except Exception as e:
            return Result.failure(e)

    @property
    def cell(self) -> CalcCell:
        return self._cell
