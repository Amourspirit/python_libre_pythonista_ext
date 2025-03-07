from __future__ import annotations
from typing import TYPE_CHECKING, Any
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind


def create_control(calc_cell: CalcCell, ctl_kind: CtlKind) -> Any:  # noqa: ANN401
    """Creates a control for the given cell and control kind."""
    builder = get_builder(calc_cell, ctl_kind)
    if ctl_kind == CtlKind.STRING:
        return CtlStr(builder.build())
    return None


def get_control(calc_cell: CalcCell) -> Any:  # noqa: ANN401
    """Gets a control for the given cell and control kind."""
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    qry = QryCtlKind(calc_cell)
    handler = QryHandlerFactory.get_qry_handler()
    ctl_kind = handler.handle(qry)
    reader = get_reader(calc_cell, ctl_kind)
    if ctl_kind == CtlKind.STRING:
        return CtlStr(reader.read())
    return None
