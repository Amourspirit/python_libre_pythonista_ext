from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.pyc.code.py_source import PySource
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryCellHasProp(LogMixin, QryCellT[bool]):
    """Checks if the cell has a custom property"""

    def __init__(self, cell: CalcCell, name: str) -> None:
        LogMixin.__init__(self)
        self._cell = cell
        self._kind = CalcQryKind.CELL
        self._name = name

    def execute(self) -> bool:
        """
        Executes the query to get if the cell contain a custom property.

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        try:
            return self._cell.has_custom_property(self._name)
        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def cell(self) -> CalcCell:
        return self._cell

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the cell query. Defaults to ``CalcQryKind.CELL``.
        """

        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
