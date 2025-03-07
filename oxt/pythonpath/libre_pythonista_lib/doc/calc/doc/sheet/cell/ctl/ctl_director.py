from __future__ import annotations
from typing import TYPE_CHECKING, Type, overload
from ooodev.calc import CalcCell

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_float import CtlFloat
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind


def _get_control_class(ctl_kind: CtlKind) -> Type[CtlBase] | None:
    """
    Gets the control class for the given control kind.

    Args:
        ctl_kind (CtlKind): The kind of control to get the class for

    Returns:
        Type[CtlBase] | None: The control class or None if not found
    """
    # Import controls here to avoid circular imports
    if TYPE_CHECKING:
        pass
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_frame_ctl import DataFrameCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_series_ctl import DataSeriesCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_tbl_ctl import DataTblCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mat_plot_figure_ctl import MatPlotFigureCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.error_ctl import ErrorCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.none_ctl import NoneCtl
        # from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.empty_ctl import EmptyCtl
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_float import CtlFloat
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_frame_ctl import DataFrameCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_series_ctl import DataSeriesCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.data_tbl_ctl import DataTblCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.mat_plot_figure_ctl import MatPlotFigureCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.error_ctl import ErrorCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.none_ctl import NoneCtl
        # from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.empty_ctl import EmptyCtl

    control_map = {
        CtlKind.STRING: CtlStr,
        CtlKind.FLOAT: CtlFloat,
        # CtlKind.INTEGER: FloatCtl,
        # CtlKind.DATA_FRAME: DataFrameCtl,
        # CtlKind.SERIES: DataSeriesCtl,
        # CtlKind.DATA_TABLE: DataTblCtl,
        # CtlKind.MAT_PLT_FIGURE: MatPlotFigureCtl,
        # CtlKind.ERROR: ErrorCtl,
        # CtlKind.NONE: NoneCtl,
        # CtlKind.EMPTY: EmptyCtl,
    }
    return control_map.get(ctl_kind)


@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.STRING]) -> CtlStr: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.FLOAT]) -> CtlFloat: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBase | None: ...


def create_control(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBase | None:
    """Creates a control for the given cell and control kind."""
    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        return None

    builder = get_builder(calc_cell, ctl_kind)
    return control_class(builder.build())


def get_control(calc_cell: CalcCell) -> CtlBase | None:
    """Gets a control for the given cell and control kind."""

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    qry = QryCtlKind(calc_cell)
    handler = QryHandlerFactory.get_qry_handler()
    ctl_kind = handler.handle(qry)
    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        return None

    reader = get_reader(calc_cell, ctl_kind)
    return control_class(reader.read())
