from __future__ import annotations
from typing import List, TYPE_CHECKING
from ooodev.calc import CalcDoc, CalcCell
from ...code.cell_cache import CellCache
from ..props.key_maker import KeyMaker
from .array_factory import get_array_helper


if TYPE_CHECKING:
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class ArrayMgr:
    def __init__(self, doc: CalcDoc) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        with self._log.indent(True):
            self._log.debug("init")
        self._doc = doc
        self._cell_cache = CellCache(self._doc)
        self._key_maker = KeyMaker()

    def get_array_cells(self) -> List[CalcCell]:
        """
        Gets all the cell if the sheet that have array formulas and are currently displayed as an array formula.

        Returns:
            List[CalcCell]: A list of CalcCell objects that have array formulas.
        """
        results: List[CalcCell] = []

        for idx, value in self._cell_cache.code_cells.items():
            sheet = self._doc.sheets[idx]
            for cell_obj in value:
                cell = sheet[cell_obj]
                if self._has_array_ability(cell):
                    results.append(cell)
        if self._log.is_debug:
            with self._log.indent(True):
                self._log.debug("get_array_cells() - %i", len(results))
        return results

    def _has_array_ability(self, cell: CalcCell) -> bool:
        try:
            key = self._key_maker.cell_array_ability_key
            if self._log.is_debug:
                self._log.debug("_has_array_ability() Key: %s", key)
                self._log.debug("_has_array_ability() Cell: %s, Sheet %s", cell.cell_obj, cell.calc_sheet.name)
            cp = cell.get_custom_property(key, False)
            if cp:
                return True
        except Exception:
            self._log.exception("_has_array_ability()")
        return False

    def update_array_cells(self) -> None:
        """
        Updates all sheet array formulas for this extension if the array size has changed.
        """
        try:
            for cell in self.get_array_cells():
                helper = get_array_helper(cell)
                if helper is None:
                    continue
                helper.update()
        except Exception:
            self._log.exception("update_array_cells()")
            raise
