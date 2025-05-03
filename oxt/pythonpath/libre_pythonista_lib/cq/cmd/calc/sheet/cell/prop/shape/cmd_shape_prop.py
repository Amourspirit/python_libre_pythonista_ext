from __future__ import annotations
from typing import TYPE_CHECKING, Union

from ooo.dyn.drawing.text_vertical_adjust import TextVerticalAdjust

if TYPE_CHECKING:
    from com.sun.star.sheet import Shape  # service
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.log.log_mixin import LogMixin

    Shape = object


class CmdShapeProp(CmdBase, LogMixin, CmdCellCtlT):
    """
    Sets Shape properties.
    If no props are passed then default props are used.

    .. code-block:: python

        default_props = {
            "Anchor": self.cell.component,
            "Decorative": False,
            "HoriOrient": 0,
            "MoveProtect": True,
            "Printable": False,
            "ResizeWithCell": True,
            "SizeProtect": False,
            "TextVerticalAdjust": TextVerticalAdjust.CENTER,
            "Visible": True,
        }
    """

    def __init__(self, cell: CalcCell, shape: Shape, props: Union[dict, None] = None) -> None:
        """Constructor

        Args:
            cell (CalcCell): Cell to set the shape for.
            shape (Shape): Shape to set the properties for.
            props (dict, optional): Properties to set. Defaults to None.
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._shape = shape
        if props is None:
            props = self._get_default_props()
        self._props = props
        self._current_state: Union[dict, None] = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _get_default_props(self) -> dict:
        d = {
            "Anchor": self.cell.component,
            "Decorative": False,
            "HoriOrient": 0,
            "MoveProtect": True,
            "Printable": False,
            "ResizeWithCell": True,
            "SizeProtect": False,
            "TextVerticalAdjust": TextVerticalAdjust.CENTER,
            "Visible": True,
        }
        return d

    def _get_original_props(self, props: dict) -> dict:
        """Gets the original properties of the shape"""
        results = {}
        for k in props:
            if hasattr(self._shape, k):
                results[k] = getattr(self._shape, k)
            else:
                self.log.debug("When getting original properties. Property not found: %s", k)
        return results

    def _set_props(self, props: dict) -> None:
        for k, v in props.items():
            if hasattr(self._shape, k):
                setattr(self._shape, k, v)
                self.log.debug("Set property: %s", k)
            else:
                self.log.debug("When setting properties. Property not found: %s", k)

    @override
    def execute(self) -> None:
        """
        Executes the command.
        """
        self.success = False
        if self._current_state is None:
            self._current_state = self._get_original_props(self._props)

        try:
            self._set_props(self._props)
            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting shape properties: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if self._current_state is None:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._set_props(self._current_state)
        self.log.debug("Successfully executed undo command.")

    @override
    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._cell
