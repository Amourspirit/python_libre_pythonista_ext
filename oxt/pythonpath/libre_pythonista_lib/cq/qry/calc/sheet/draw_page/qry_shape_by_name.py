from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.exceptions.ex import ShapeMissingError
from ooodev.calc import CalcSheet, SpreadsheetDrawPage
from ooodev.draw.shapes import DrawShape

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryShapeByName(QryBase, LogMixin, QrySheetT[DrawShape[SpreadsheetDrawPage[CalcSheet]] | None]):
    def __init__(self, sheet: CalcSheet, shape_name: str) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET
        self._shape_name = shape_name
        self._sheet = sheet

    def execute(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """
        Executes the query to get the shape.

        Returns:
            DrawShape[SpreadsheetDrawPage[CalcSheet]] | None: The shape if successful, otherwise None.
        """

        try:
            dp = self._sheet.draw_page
            shape = dp.find_shape_by_name(self._shape_name)
            return shape
        except ShapeMissingError:
            self.log.debug("Shape not found: %s", self._shape_name)
        except Exception:
            self.log.exception("Error getting shape")
        return None

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
