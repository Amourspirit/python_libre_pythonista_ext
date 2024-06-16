from __future__ import annotations
from ooodev.calc import CalcCell


class CellDispatchState:
    def __init__(self, cell: CalcCell):
        self._cell = cell
        self._cache = {}

    def is_dispatch_enabled(self, cmd: str) -> bool:
        if cmd == ".uno:libre_pythonista.calc.menu.code.edit":
            if not self.sheet_locked:
                return True
            return not self.cell_locked
        return True

    # region Properties
    @property
    def sheet_locked(self) -> bool:
        key = "sheet_locked"
        if key not in self._cache:
            self._cache[key] = self._cell.calc_sheet.is_sheet_protected()
        return self._cache[key]

    @property
    def cell_locked(self) -> bool:
        key = "cell_locked"
        if key not in self._cache:
            self._cache[key] = self._cell.cell_protection.is_locked
        return self._cache[key]

    # endregion Properties
