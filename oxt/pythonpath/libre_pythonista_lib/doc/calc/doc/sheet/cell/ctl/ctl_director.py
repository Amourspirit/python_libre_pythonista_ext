from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type, overload
from ooodev.calc import CalcCell

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_t import CmdHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_t import QryHandlerT
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.general.cmd_batch import CmdBatch
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_base import CtlBase
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_float import CtlFloat
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_int import CtlInt
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_pd_df import CtlPdDf
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_pd_series import CtlPdSeries
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_data_tbl import CtlDataTbl
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_empty import CtlEmpty
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_error import CtlError
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_none import CtlNone
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_mat_plot_fig import CtlMatPlotFig
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import (
        CmdRemoveCtlProps,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.draw_page.cmd_del_shape_by_name import CmdDelShapeByName
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    # from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener_del import (
    #     CmdCodeListenerDel,
    # )

else:
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.remove.cmd_remove_ctl_props import CmdRemoveCtlProps
    from libre_pythonista_lib.cq.cmd.calc.sheet.draw_page.cmd_del_shape_by_name import CmdDelShapeByName
    from libre_pythonista_lib.cq.cmd.general.cmd_batch import CmdBatch
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_ctl_kind import QryCtlKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
    from libre_pythonista_lib.kind.ctl_kind import CtlKind
    from libre_pythonista_lib.utils.result import Result
    # from libre_pythonista_lib.cq.cmd.calc.sheet.cell.listener.cmd_code_listener_del import CmdCodeListenerDel

    CmdHandlerT = Any
    QryHandlerT = Any


def _get_control_class(ctl_kind: CtlKind) -> Type[CtlBase] | None:
    """
    Gets the control class for the given control kind.

    Args:
        ctl_kind (CtlKind): The kind of control to get the class for

    Returns:
        Type[CtlBase] | None: The control class or None if not found
    """
    # Import controls here to avoid circular imports
    if not TYPE_CHECKING:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_str import CtlStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_float import CtlFloat
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_int import CtlInt
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_pd_df import CtlPdDf
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_pd_series import CtlPdSeries
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_data_tbl import CtlDataTbl
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_empty import CtlEmpty
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_error import CtlError
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_none import CtlNone
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_mat_plot_fig import CtlMatPlotFig

    control_map = {
        CtlKind.STRING: CtlStr,
        CtlKind.FLOAT: CtlFloat,
        CtlKind.INTEGER: CtlInt,
        CtlKind.DATA_FRAME: CtlPdDf,
        CtlKind.SERIES: CtlPdSeries,
        CtlKind.DATA_TABLE: CtlDataTbl,
        CtlKind.EMPTY: CtlEmpty,
        CtlKind.ERROR: CtlError,
        CtlKind.NONE: CtlNone,
        CtlKind.MAT_PLT_FIGURE: CtlMatPlotFig,
    }
    return control_map.get(ctl_kind)


def _get_cmd_handler() -> CmdHandlerT:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory
    else:
        from libre_pythonista_lib.cq.cmd.cmd_handler_factory import CmdHandlerFactory

    return CmdHandlerFactory.get_cmd_handler()


def _get_qry_handler() -> QryHandlerT:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    return QryHandlerFactory.get_qry_handler()


@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.STRING]) -> CtlStr: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.INTEGER]) -> CtlInt: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.FLOAT]) -> CtlFloat: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.DATA_FRAME]) -> CtlPdDf: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.SERIES]) -> CtlPdSeries: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.DATA_TABLE]) -> CtlDataTbl: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.EMPTY]) -> CtlEmpty: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.ERROR]) -> CtlError: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.NONE]) -> CtlNone: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.MAT_PLT_FIGURE]) -> CtlMatPlotFig: ...
@overload
def create_control(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBase | None: ...


def create_control(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBase | None:
    """Creates a control for the given cell and control kind."""
    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        return None

    builder = get_builder(calc_cell, ctl_kind)
    return control_class(builder.build())


def remove_control(calc_cell: CalcCell) -> bool:
    """
    Removes a control for the given cell and control kind.

    Args:
        calc_cell (CalcCell): The cell to remove the control from

    Returns:
        bool: True if the control was removed, False otherwise
    """
    ctl = get_control(calc_cell)
    if ctl is None:
        return True
    shape_name = ctl.get_shape_name()
    if shape_name is None:
        return True

    cmd_handler = _get_cmd_handler()
    # remove control properties from cell.
    cmd_del_props = CmdRemoveCtlProps(ctl.ctl)
    cmd_del_shape = CmdDelShapeByName(calc_cell.calc_sheet, shape_name)
    # cmd_del_listener = CmdCodeListenerDel(calc_cell)
    batch = CmdBatch(cmd_del_shape, cmd_del_props)
    cmd_handler.handle(batch)
    if not batch.success:
        cmd_handler.undo()
    return batch.success


def get_control(calc_cell: CalcCell) -> CtlBase | None:
    """Gets a control for the given cell and control kind."""

    qry = QryCtlKind(calc_cell)
    handler = _get_qry_handler()
    result = handler.handle(qry)
    if Result.is_failure(result):
        return None
    ctl_kind = result.data

    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        return None

    reader = get_reader(calc_cell, ctl_kind)
    return control_class(reader.read())
