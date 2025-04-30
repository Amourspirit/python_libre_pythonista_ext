from __future__ import annotations

from typing import Any, Iterable, TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.helper.dot_dict import DotDict


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.log.log_mixin import LogMixin

# tested in: tests/test_cmd_qry/test_cell/prop/test_cell_prop_values.py


class QryCellPropValues(QryBase, LogMixin, QryCellT[DotDict[Any]]):
    """Gets the names and values of a custom property of a cell"""

    def __init__(self, cell: CalcCell, prop_names: Iterable[str], default: Any = NULL) -> None:  # noqa: ANN401
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
            default (Any, optional): Default value to return if the custom property is not found. Defaults to ``NULL``.
            prop_names (Iterable[str]): Names of the custom properties.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._default = default
        self._prop_names = prop_names
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_prop_value(self, name: str) -> Any:  # noqa: ANN401
        qry = QryCellPropValue(cell=self._cell, name=name, default=self._default)
        return self._execute_qry(qry)

    def execute(self) -> DotDict[Any]:  # noqa: ANN401
        """
        Executes the query to get the cell custom property values.

        Returns:
            DotDict: The custom property values if successful, otherwise an empty DotDict.

        Note:
            ``DotDict`` can be imported from ``ooodev.utils.helper.dot_dict.DotDict``.
        """
        # DotDict[Any]() is not supported in Python 3.8 only 3.9+
        dd: DotDict[Any] = DotDict()
        try:
            if not self._prop_names:
                return dd
            for name in self._prop_names:
                dd[name] = self._get_prop_value(name)
            return dd
        except Exception:
            self.log.exception("Error executing query")
        return dd

    @property
    def cell(self) -> CalcCell:
        return self._cell
