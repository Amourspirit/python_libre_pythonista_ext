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
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_df import CtlReaderPdDf
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_series import (
        CtlReaderPdSeries,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_data_tbl import (
        CtlReaderDataTbl,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_empty import CtlReaderEmpty
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_error import CtlReaderError
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_none import CtlReaderNone
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_mat_plot_fig import (
        CtlReaderMatPlotFig,
    )
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder.py


def _get_kind(calc_cell: CalcCell) -> CtlKind:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    qry = QryCtlKind(calc_cell)
    handler = QryHandlerFactory.get_qry_handler()
    result = handler.handle(qry)
    if Result.is_failure(result):
        return CtlKind.UNKNOWN
    return result.data


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
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_df import CtlReaderPdDf
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_series import CtlReaderPdSeries
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_data_tbl import CtlReaderDataTbl
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_empty import CtlReaderEmpty
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_error import CtlReaderError
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_none import CtlReaderNone
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_mat_plot_fig import (
            CtlReaderMatPlotFig,
        )

    control_map = {
        CtlKind.STRING: CtlReaderStr,
        CtlKind.INTEGER: CtlReaderInt,
        CtlKind.FLOAT: CtlReaderFloat,
        CtlKind.DATA_FRAME: CtlReaderPdDf,
        CtlKind.SERIES: CtlReaderPdSeries,
        CtlKind.DATA_TABLE: CtlReaderDataTbl,
        CtlKind.EMPTY: CtlReaderEmpty,
        CtlKind.ERROR: CtlReaderError,
        CtlKind.NONE: CtlReaderNone,
        CtlKind.MAT_PLT_FIGURE: CtlReaderMatPlotFig,
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
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.DATA_FRAME]) -> CtlReaderPdDf: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.SERIES]) -> CtlReaderPdSeries: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.DATA_TABLE]) -> CtlReaderDataTbl: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.EMPTY]) -> CtlReaderEmpty: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.ERROR]) -> CtlReaderError: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.NONE]) -> CtlReaderNone: ...
@overload
def get_reader(calc_cell: CalcCell, kind: Literal[CtlKind.MAT_PLT_FIGURE]) -> CtlReaderMatPlotFig: ...
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
