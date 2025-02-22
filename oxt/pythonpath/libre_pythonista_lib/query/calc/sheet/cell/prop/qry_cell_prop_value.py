from __future__ import annotations


from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell
from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryCellPropValue(LogMixin, QryCellT[Any]):
    """Gets the value of a custom property of a cell"""

    def __init__(self, cell: CalcCell, name: str, default: Any = NULL_OBJ) -> None:  # noqa: ANN401
        """Constructor

        Args:
            cell (CalcCell): Cell to query.
            name (str): Name of the custom property.
            default (Any, optional): Default value to return if the custom property is not found. Defaults to ``NULL_OBJ``.
        """
        LogMixin.__init__(self)
        self._cell = cell
        self._name = name
        self._kind = CalcQryKind.SIMPLE
        self._default = default

    def execute(self) -> Any:  # noqa: ANN401
        """
        Executes the query to get the cell custom property value.

        Returns:
            Any: The custom property value if successful, otherwise Default or ``NULL_OBJ``.
                If no default is provided, ``NULL_OBJ`` is returned when the query fails.

        Note:
            ``NULL_OBJ`` can be imported from ``ooodev.utils.gen_util``.
        """

        try:
            return self._cell.get_custom_property(self._name, default=self._default)
        except AttributeError as e:
            self.log.error("Error executing query, Missing Attribute. Error: %s", e)
        except Exception:
            self.log.exception("Error executing query")
        return NULL_OBJ

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.SIMPLE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
