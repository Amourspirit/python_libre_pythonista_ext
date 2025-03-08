from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import create_control
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import get_control
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import create_control
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_director import get_control
    from libre_pythonista_lib.kind.ctl_kind import CtlKind


class CellItem:
    def __init__(self, cell: CalcCell) -> None:
        self._cell = cell
        self._qry_handler = QryHandlerFactory.get_qry_handler()

    def has_control(self) -> bool:
        ctl_kind = self.get_control_kind()
        return ctl_kind != CtlKind.UNKNOWN

    def get_control_kind(self) -> CtlKind:
        qry = QryCtlKind(self._cell)
        return self._qry_handler.handle(qry)

    def add_default_control(self) -> Any:
        return create_control(self._cell, CtlKind.STRING)

    def get_control(self) -> Any:
        return get_control(self._cell)
