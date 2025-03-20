from __future__ import annotations
from typing import TYPE_CHECKING, Type, overload

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_str import CtlReaderStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_int import CtlReaderInt
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_float import CtlReaderFloat
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind

    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder_str.py


def _get_kind(calc_cell: CalcCell) -> CtlKind:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    qry = QryCtlKind(calc_cell)
    handler = QryHandlerFactory.get_qry_handler()
    ctl_kind = handler.handle(qry)
    return ctl_kind


def _get_control_class(ctl_kind: CtlKind) -> Type[CtlReader] | None:
    """
    Gets the control class for the given control kind.

    Args:
        ctl_kind (CtlKind): The kind of control to get the class for

    Returns:
        Type[CtlBase] | None: The control class or None if not found
    """
    # Import controls here to avoid circular imports
    if not TYPE_CHECKING:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_str import CtlReaderStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_int import CtlReaderInt
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_float import CtlReaderFloat

    control_map = {
        CtlKind.STRING: CtlReaderStr,
        CtlKind.INTEGER: CtlReaderInt,
        CtlKind.FLOAT: CtlReaderFloat,
    }
    return control_map.get(ctl_kind)


@overload
def get_reader(calc_cell: CalcCell) -> CtlReaderStr: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.STRING]) -> CtlReaderStr: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.INTEGER]) -> CtlReaderInt: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.FLOAT]) -> CtlReaderFloat: ...
@overload
def get_reader(calc_cell: CalcCell, kind: CtlKind | None = None) -> CtlReader: ...


def get_reader(calc_cell: CalcCell, kind: CtlKind | None = None) -> CtlReader:
    """
    Gets a reader for the given cell and control kind.

    Args:
        calc_cell (CalcCell): The cell to get the reader for.
        kind (CtlKind, optional): The kind of control to get the reader for. Defaults to None.

    Raises:
        ValueError: If the kind is not valid.

    Returns:
        CtlReader: The reader for the given cell and control kind.
    """
    if kind is None:
        kind = _get_kind(calc_cell)

    control_class = _get_control_class(kind)
    if control_class is None:
        raise ValueError("Invalid control kind")

    reader = control_class(calc_cell)
    return reader
