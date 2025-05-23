from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_key_maker import QryKeyMaker
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryCodeName(QryBase, QryCellT[Union[Result[str, None], Result[None, Exception]]]):
    """Gets the code name of the cell such as ``id_l6fiSBIiNVcncf`` or empty string if not exists."""

    def __init__(self, cell: CalcCell) -> None:
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell

    def execute(self) -> Union[Result[str, None], Result[None, Exception]]:
        """
        Executes the query and gets the code name of the cell.

        Returns:
            Result: Success with code name or Failure with Exception
        """
        qry_km = QryKeyMaker()
        km = self._execute_qry(qry_km)
        qry_state = QryCellPropValue(
            cell=self._cell, name=km.cell_code_name, default=self._cell.extra_data.get("code_name", "")
        )
        result = self._execute_qry(qry_state)
        if result:
            if not "code_name" in self._cell.extra_data:
                self._cell.extra_data["code_name"] = result
            return Result.success(result)
        return Result.failure(Exception("Code name not found"))

    @property
    def cell(self) -> CalcCell:
        return self._cell
