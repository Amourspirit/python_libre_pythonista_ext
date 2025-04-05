from __future__ import annotations
from typing import cast, List, Tuple, TYPE_CHECKING
from pathlib import Path

from ooodev.units import UnitMM100
from ooodev.utils.gen_util import NULL_OBJ
from ooodev.utils.kind.drawing_shape_kind import DrawingShapeKind
from ooodev.calc import CalcCell, CalcSheet
from ooodev.draw.shapes.draw_shape import DrawShape
from ooodev.calc import SpreadsheetDrawPage

if TYPE_CHECKING:
    from ooodev.utils.type_var import PathOrStr
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.utils.custom_ext import override
    from libre_pythonista_lib.cq.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.cmd_cell_t import CmdCellT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.cq.qry.config.qry_shape_name_img import QryShapeNameImg
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.qry_ctl_cell_size_pos import QryCtlCellSizePos
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_code_name import QryCodeName
    from libre_pythonista_lib.cq.qry.calc.sheet.draw_page.qry_shape_by_name import QryShapeByName
    from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name import CmdCodeName
    from libre_pythonista_lib.utils.result import Result


class CmdAddImageLinked(CmdBase, LogMixin, CmdCellT):
    """
    Command to add a linked image to a cell in a spreadsheet.

    This command handles adding an image that is linked to a specific cell, including:
    - Setting a unique code name for the cell if not already present
    - Managing existing images in the cell (removing old ones before adding new ones)
    - Configuring image properties like anchoring and resize behavior
    - Supporting undo operations

    Attributes:
        kind (CalcCmdKind): Set to CELL to indicate this is a cell-level command
        _fnm (PathOrStr): Path to the image file to be linked
        _cell (CalcCell): The target cell where the image will be added
        _shape_name (str): Name of the shape (image) to be added
        _code_name (str): Unique code name for the cell
        _success_cmds (List[CmdCellT]): List of successfully executed sub-commands
        _current_shape (DrawShape | None): Existing shape in the cell, if any
        _new_shape (DrawShape | None): Newly added shape
    """

    def __init__(self, cell: CalcCell, fnm: PathOrStr) -> None:
        """
        Initialize the command.

        Args:
            cell: Target cell where the image will be added
            fnm: Path to the image file to be linked
        """
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcCmdKind.CELL
        self._fnm = fnm
        self._cell = cell
        self._shape_name = cast(str, None)
        self._code_name = cast(str, None)
        self._success_cmds: List[CmdCellT] = []
        self._current_shape = cast(DrawShape[SpreadsheetDrawPage[CalcSheet]] | None, NULL_OBJ)
        self._new_shape: DrawShape[SpreadsheetDrawPage[CalcSheet]] | None = None
        self.log.debug("init done for cell %s", cell.cell_obj)

    def _validate(self) -> bool:
        if not self._fnm:
            self.log.error("Validation error. fnm attribute is empty.")
            return False
        fnm_pth: Path = Path(self._fnm) if isinstance(self._fnm, str) else self._fnm  # type: ignore
        if not fnm_pth.exists():
            self.log.error("Validation error. fnm attribute does not exist.")
            return False
        return True

    def _cmd_code_name(self) -> bool:
        """
        Sets a unique code name for the cell.

        Returns:
            bool: True if code name was successfully set, False otherwise
        """
        cmd = CmdCodeName(cell=self.cell, overwrite_existing=False)
        self._execute_cmd(cmd)
        if cmd.success:
            self._success_cmds.append(cmd)
            return True
        return False

    def _qry_size_pos(self) -> Tuple[UnitMM100, UnitMM100, UnitMM100, UnitMM100]:
        """
        Gets the position and size for the image based on the cell dimensions.

        Returns:
            Tuple containing x, y coordinates and width, height in MM100 units
        """
        qry = QryCtlCellSizePos(cell=self.cell, merged=True)
        size_pos = self._execute_qry(qry)
        return (
            size_pos.x,
            size_pos.y,
            size_pos.width,
            size_pos.height,
        )

    def _qry_code_name(self) -> str:
        """
        Gets or sets the code name for the cell.

        Returns:
            str: The cell's code name

        Raises:
            Exception: If code name cannot be retrieved or set
        """
        qry = QryCodeName(cell=self.cell)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        if self._cmd_code_name():
            result = self._execute_qry(qry)
            if Result.is_success(result):
                return result.data
        raise result.error

    def _qry_shape_img_name(self, code_name: str) -> str:
        """
        Generates a unique shape name for the image based on the cell's code name.

        Args:
            code_name: The cell's code name

        Returns:
            str: Generated shape name for the image
        """
        qry = QryShapeNameImg(code_name=code_name)
        return self._execute_qry(qry)

    def _qry_shape_by_name(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]] | None:
        """
        Retrieves an existing shape by its name from the sheet.

        Returns:
            DrawShape if found, None otherwise
        """
        qry = QryShapeByName(sheet=self.cell.calc_sheet, shape_name=self._shape_name)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    def _set_shape_props(self, shape: DrawShape[SpreadsheetDrawPage[CalcSheet]]) -> None:
        """
        Sets standard properties for the image shape.

        Properties include anchor, visibility, protection settings, and resize behavior.

        Args:
            shape: The shape whose properties are to be set
        """
        data = {
            "Anchor": self.cell.component,
            "Decorative": False,
            "HoriOrient": 0,
            "MoveProtect": True,
            "Printable": False,
            "ResizeWithCell": True,
            "SizeProtect": False,
            "Visible": True,
        }
        x_shape = shape.component
        for key, value in data.items():
            if hasattr(x_shape, key):
                setattr(x_shape, key, value)

    def _set_shape_name(self, shape: DrawShape[SpreadsheetDrawPage[CalcSheet]]) -> None:
        """
        Sets the name of the shape.

        Args:
            shape: The shape to be named
        """
        shape.name = self._shape_name

    def _add_known_cell_image_linked(self, shape: DrawShape[SpreadsheetDrawPage[CalcSheet]]) -> None:
        """
        Adds an existing shape to the sheet's draw page.

        Args:
            shape: The shape to be added
        """
        sheet = self.cell.calc_sheet
        sheet.draw_page.add(shape.component)

    def _remove_known_cell_image_linked(self, shape: DrawShape[SpreadsheetDrawPage[CalcSheet]]) -> None:
        """
        Removes a shape from the sheet's draw page.

        Args:
            shape: The shape to be removed
        """
        sheet = self.cell.calc_sheet
        sheet.draw_page.remove(shape.component)

    def _add_cell_image_linked(self) -> DrawShape[SpreadsheetDrawPage[CalcSheet]]:
        """
        Creates and configures a new linked image shape.

        Returns:
            DrawShape: The newly created image shape
        """
        sheet = self.cell.calc_sheet
        shape = sheet.draw_page.add_shape(DrawingShapeKind.GRAPHIC_OBJECT_SHAPE, *self._qry_size_pos())
        shape.set_image(self._fnm)
        self.log.debug("CellImg: insert_cell_image_linked(): Image set  %s", self._fnm)
        return shape

    @override
    def execute(self) -> None:
        """
        Executes the command to add a linked image to the cell.

        The operation includes:
        1. Getting/setting cell code name
        2. Generating shape name
        3. Removing existing shape if present
        4. Adding and configuring new shape
        """
        self._success_cmds.clear()
        self.success = False
        if not self._validate():
            self.log.error("Validation error occurred. Unable to execute command.")
            return

        try:
            if self._code_name is None:
                self._code_name = self._qry_code_name()

            if self._shape_name is None:
                self._shape_name = self._qry_shape_img_name(self._code_name)

            if self._current_shape is NULL_OBJ:
                self._current_shape = self._qry_shape_by_name()
                if self._current_shape:
                    # if there is a shape remove it before adding a new one.
                    self.log.debug("Removing cell image for %s", self.cell.cell_obj)
                    self._remove_known_cell_image_linked(self._current_shape)

            self._new_shape = self._add_cell_image_linked()
            self._set_shape_props(self._new_shape)
            self._set_shape_name(self._new_shape)
        except Exception as e:
            self.log.exception("Error setting cell Code: %s", e)
            for cmd in reversed(self._success_cmds):
                self._execute_cmd_undo(cmd)
            self._success_cmds.clear()
            return
        self.log.debug("Successfully executed command for cell %s.", self.cell.cell_obj)
        self.success = True

    def _undo(self) -> None:
        """
        Internal method to undo the command's changes.

        Reverts all successful sub-commands and restores the previous image if any.
        """
        try:
            for cmd in reversed(self._success_cmds):
                self._execute_cmd_undo(cmd)
            self._success_cmds.clear()

            if self._current_shape and self._new_shape:
                self._remove_known_cell_image_linked(self._new_shape)
                self._add_known_cell_image_linked(self._current_shape)

                self._new_shape = None

            if self._new_shape:
                self._remove_known_cell_image_linked(self._new_shape)

            self._new_shape = None
            self._current_shape = None

            self.log.debug("Successfully executed undo command.")
        except Exception:
            self.log.exception("Error undoing cell Code")

    @override
    def undo(self) -> None:
        """
        Public method to undo the command if it was successful.
        """
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        """
        Gets the target cell.

        Returns:
            CalcCell: The cell where the image is being added
        """
        return self._cell
