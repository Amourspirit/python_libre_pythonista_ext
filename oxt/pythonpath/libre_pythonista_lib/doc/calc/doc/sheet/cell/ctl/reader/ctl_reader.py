from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_array_ability import QryArrayAbility
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
else:
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_addr import QryAddr
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_array_ability import QryArrayAbility
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl


class CtlReader(List[QryT], LogMixin, ABC):
    def __init__(self, cell: CalcCell) -> None:
        list.__init__(self)
        LogMixin.__init__(self)
        self.ctl = Ctl()
        self.ctl.cell = cell
        self._success = False
        self._handler = QryHandler()

    def _append_base_query(self) -> None:
        self.clear()
        self.append(QryCodeName(self.cell, self.ctl))
        self.append(QryAddr(self.cell, self.ctl))
        self.append(QryArrayAbility(cell=self.cell, ctl=self.ctl))
        self.append(QryCtlKind(cell=self.cell, ctl=self.ctl))
        self.append_query()

    @abstractmethod
    def append_query(self) -> None:
        """Appends queries to the list of queries to be executed."""
        ...

    def _execute(self) -> None:
        self._success = False
        try:
            for cmd in self:
                _ = self._handler.handle(cmd)
        except Exception as e:
            self.log.exception("An unexpected error occurred: %s", e)
            return

        self.log.debug("Successfully executed queries.")

    def read(self) -> Ctl:
        """Reads the control from the cell"""
        self._append_base_query()
        self._execute()
        return self.ctl

    @property
    def cell(self) -> CalcCell:
        return self.ctl.cell
