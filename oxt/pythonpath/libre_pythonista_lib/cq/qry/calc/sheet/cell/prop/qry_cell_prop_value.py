from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.utils.null import NULL
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryCellPropValue(QryBase, LogMixin, QryCellT[Any]):
    """Gets the value of a custom property of a cell"""

    def __init__(self, cell: CalcCell, name: str, default: Any = NULL) -> None:  # noqa: ANN401
        """Constructor

        Args:
            cell (CalcCell): Cell to query.

            name (str): Name of the custom property.
            default (Any, optional): Default value to return if the custom property is not found. Defaults to ``NULL``.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._name = name
        self._default = default
        self.log.debug("init done for cell %s", cell.cell_obj)

    def execute(self) -> Any:  # noqa: ANN401
        """
        Executes the query to get the cell custom property value.

        Returns:
            Any: The custom property value if successful, otherwise Default or ``NULL``.
                If no default is provided, ``NULL`` is returned when the query fails.
        """

        try:
            return self._cell.get_custom_property(self._name, default=self._default)
        except AttributeError:
            self.log.debug("Missing Attribute %s. Returning Default.", self._name)
        except Exception:
            self.log.exception("Error executing query")
        return self._default

    @property
    def cell(self) -> CalcCell:
        """
        Gets the cell being queried.

        Returns:
            CalcCell: The cell instance this query operates on.
        """
        return self._cell
