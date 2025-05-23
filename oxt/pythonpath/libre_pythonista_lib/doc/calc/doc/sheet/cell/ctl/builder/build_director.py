from __future__ import annotations
from typing import TYPE_CHECKING, Type, overload, Union

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_int import CtlBuilderInt
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_float import (
        CtlBuilderFloat,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder import CtlBuilder
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_df import (
        CtlBuilderPdDf,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_series import (
        CtlBuilderPdSeries,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_data_tbl import (
        CtlBuilderDataTbl,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_empty import (
        CtlBuilderEmpty,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_error import (
        CtlBuilderError,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_none import (
        CtlBuilderNone,
    )
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_mat_plot_fig import (
        CtlBuilderMatPlotFig,
    )
else:
    from libre_pythonista_lib.kind.ctl_kind import CtlKind

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder.py


def _get_control_class(ctl_kind: CtlKind) -> Union[Type[CtlBuilder], None]:
    """
    Gets the control class for the given control kind.

    Args:
        ctl_kind (CtlKind): The kind of control to get the class for

    Returns:
        Type[CtlBase], None: The control class or None if not found
    """
    # Import controls here to avoid circular imports
    if not TYPE_CHECKING:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_int import CtlBuilderInt
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_float import CtlBuilderFloat
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_df import CtlBuilderPdDf
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_series import CtlBuilderPdSeries
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_data_tbl import CtlBuilderDataTbl
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_empty import CtlBuilderEmpty
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_error import CtlBuilderError
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_none import CtlBuilderNone
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_mat_plot_fig import (
            CtlBuilderMatPlotFig,
        )

    control_map = {
        CtlKind.STRING: CtlBuilderStr,
        CtlKind.FLOAT: CtlBuilderFloat,
        CtlKind.INTEGER: CtlBuilderInt,
        CtlKind.DATA_FRAME: CtlBuilderPdDf,
        CtlKind.SERIES: CtlBuilderPdSeries,
        CtlKind.DATA_TABLE: CtlBuilderDataTbl,
        CtlKind.EMPTY: CtlBuilderEmpty,
        CtlKind.ERROR: CtlBuilderError,
        CtlKind.NONE: CtlBuilderNone,
        CtlKind.MAT_PLT_FIGURE: CtlBuilderMatPlotFig,
    }
    return control_map.get(ctl_kind)


@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.STRING]) -> CtlBuilderStr: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.INTEGER]) -> CtlBuilderInt: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.FLOAT]) -> CtlBuilderFloat: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.DATA_FRAME]) -> CtlBuilderPdDf: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.SERIES]) -> CtlBuilderPdSeries: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.DATA_TABLE]) -> CtlBuilderDataTbl: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.EMPTY]) -> CtlBuilderEmpty: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.ERROR]) -> CtlBuilderError: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.NONE]) -> CtlBuilderNone: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: Literal[CtlKind.MAT_PLT_FIGURE]) -> CtlBuilderMatPlotFig: ...
@overload
def get_builder(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBuilder: ...


def get_builder(calc_cell: CalcCell, ctl_kind: CtlKind) -> CtlBuilder:
    control_class = _get_control_class(ctl_kind)
    if control_class is None:
        raise ValueError("Invalid control kind")
    builder = control_class(calc_cell)
    return builder
