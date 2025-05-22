from __future__ import annotations
from typing import TYPE_CHECKING, Union

from ooodev.exceptions.ex import ShapeMissingError
from ooodev.calc import CalcSheet, SpreadsheetDrawPage
from ooodev.draw.shapes import DrawShape

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result


class QryShapeByName(
    QryBase,
    LogMixin,
    QrySheetT[Union[Result[DrawShape[SpreadsheetDrawPage[CalcSheet]], None], Result[None, Exception]]],
):
    def __init__(self, sheet: CalcSheet, shape_name: str) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SHEET
        self._shape_name = shape_name
        self._sheet = sheet
        self.log.debug("init done for sheet %s for shape %s", sheet.name, shape_name)

    def execute(self) -> Union[Result[DrawShape[SpreadsheetDrawPage[CalcSheet]], None], Result[None, Exception]]:
        """
        Executes the query to get the shape.

        Returns:
            Result: Success with shape or Failure with Exception
        """
        try:
            dp = self._sheet.draw_page
            shape = dp.find_shape_by_name(self._shape_name)
            return Result.success(shape)
        except ShapeMissingError as e:
            self.log.debug("Shape not found: %s", self._shape_name)
            return Result.failure(e)
        except Exception as e:
            self.log.exception("Error getting shape")
            return Result.failure(e)

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet
