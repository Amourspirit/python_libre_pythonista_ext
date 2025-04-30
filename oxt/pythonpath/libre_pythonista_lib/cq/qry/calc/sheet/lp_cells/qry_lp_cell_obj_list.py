from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.calc import CalcSheet


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.sheet.qry_sheet_t import QrySheetT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.config.qry_cell_cp_codename import QryCellCpCodeName


class QryLpCellObjList(QryBase, LogMixin, QrySheetT[List[CellObj]]):
    def __init__(self, sheet: CalcSheet) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._sheet = sheet
        self.log.debug("init done for sheet %s", sheet.name)

    def _qry_cell_cp_code_name(self) -> str:
        """
        Query class that retrieves the codename from configuration.
        Something like ``libre_pythonista_codename``

        Returns:
            str: The codename used for filtering cells.
        """
        qry = QryCellCpCodeName()
        return self._execute_qry(qry)

    def _get_cells(self) -> List[CellObj]:
        filter_key = self._qry_cell_cp_code_name()
        code_cells: List[CellObj] = []

        sheet = self._sheet
        # deleted cells will not be in the custom properties

        code_cell = sheet.custom_cell_properties.get_cell_properties(filter_key)  # sorted order
        for key in code_cell:
            code_cells.append(key)

        return code_cells

    def execute(self) -> List[CellObj]:
        try:
            return self._get_cells()
        except Exception:
            self.log.exception("Error executing query")
        return []

    @property
    def sheet(self) -> CalcSheet:
        """The sheet being queried."""
        return self._sheet
