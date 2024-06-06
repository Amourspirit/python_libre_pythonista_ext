from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Union
import contextlib
import hashlib
import uno
from ooo.dyn.table.cell_address import CellAddress
from ooo.dyn.beans.property_attribute import PropertyAttributeEnum
from ooodev.calc import CalcDoc
from ooodev.form.controls.form_ctl_hidden import FormCtlHidden
from ooodev.utils import gen_util as gUtil
from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from com.sun.star.sheet import SheetCell

    from com.sun.star.table import Cell
    from com.sun.star.table import CellProperties
    from com.sun.star.style import CharacterProperties
    from com.sun.star.style import ParagraphProperties
    from com.sun.star.sheet import SheetCellRange
    from com.sun.star.table import CellRange

    ScCellObj = Union[
        SheetCell, Cell, CellProperties, CharacterProperties, ParagraphProperties, SheetCellRange, CellRange
    ]
    ScCellRangeObj = Union[SheetCellRange, CellRange, CellProperties, CharacterProperties, ParagraphProperties]
else:
    ScCellObj = Any
    ScCellRangeObj = Any


class PythonCode:
    def __init__(self, ctx: Any, verify_is_formula: bool = False):
        self._ctx = ctx
        self._hidden_name = "PythonCodeHiddenID"
        self._verify_is_formula = verify_is_formula
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        self._doc = CalcDoc.from_current_doc()
        self._addr = self.get_formula_addr()

    def _is_py_formula(self, formula: Any) -> bool:
        if not formula:
            self._logger.debug("_is_py_formula: formula is None")
            return False
        if not isinstance(formula, str):
            self._logger.debug("_is_py_formula: formula is not str")
            return False
        return formula.lower().startswith(("=py(", "{=py(")) and formula.endswith((")", ")}"))

    def get_formula_addr(self) -> CellAddress | None:
        sel = self._doc.get_selection()
        if sel is None:
            self._logger.debug("get_formula_addr: sel is None")
            with contextlib.suppress(Exception):
                addr = self._doc.get_selected_cell_addr()
                calc_cell = self._doc.sheets[addr.Sheet][addr]
                cell = calc_cell.component
                if self._is_py_formula(cell.getFormula()):
                    self._logger.debug("get_formula_addr: got cell from doc.get_selected_cell_addr()")
                    return addr
            self._logger.debug("get_formula_addr: return None")
            return None

        # is this cell selection?
        name = sel.getImplementationName()
        if name == "ScCellObj":
            self._logger.debug("get_formula_addr: cell selection is ScCellObj")
            sel_cell = cast(ScCellObj, sel)
            if not self._verify_is_formula:
                self._logger.debug("get_formula_addr: return sel_cell.getCellAddress() without verifying formula")
                return sel_cell.getCellAddress()  # type: ignore
            formula = sel_cell.getFormula()  # type: ignore
            if not formula:
                self._logger.debug("get_formula_addr: sel_cell.getFormula() is empty")
                return None
            if self._is_py_formula(formula):
                self._logger.debug("get_formula_addr: return sel_cell.getCellAddress()")
                return sel_cell.getCellAddress()  # type: ignore
        if name == "ScCellRangeObj":
            self._logger.debug("get_formula_addr: cell selection is ScCellRangeObj")
            sel_cells = cast(ScCellRangeObj, sel)
            if not self._verify_is_formula:
                self._logger.debug("get_formula_addr: return sel_cells.getRangeAddress() without verifying formula")
                rng_addr = sel_cells.getRangeAddress()  # type: ignore
                self._logger.debug(
                    f"get_formula_addr: return CellAddress({rng_addr.Sheet}, {rng_addr.StartColumn}, {rng_addr.StartRow})"
                )
                return CellAddress(rng_addr.Sheet, rng_addr.StartColumn, rng_addr.StartRow)
            formula = sel_cells.getArrayFormula()  # type: ignore
            self._logger.debug(f"get_formula_addr: formula:{formula}")
            if self._is_py_formula(formula):
                rng_addr = sel_cells.getRangeAddress()  # type: ignore
                self._logger.debug(
                    f"get_formula_addr: return CellAddress({rng_addr.Sheet}, {rng_addr.StartColumn}, {rng_addr.StartRow})"
                )
                return CellAddress(rng_addr.Sheet, rng_addr.StartColumn, rng_addr.StartRow)
        self._logger.debug("get_formula_addr: return None")
        return None

    def safe_filename_hash(self, *data: str) -> str:
        # Create a new hash object
        if not data:
            return ""
        hash_object = hashlib.sha256()

        # Update the hash object with the data you want to hash
        s = "".join(data)
        hash_object.update(s.encode("utf-8"))

        # Get the hexadecimal representation of the hash
        # prepend _ to the hash so it can be imported as a module
        hash_hex = "_" + hash_object.hexdigest()

        return hash_hex[:10]  # limit to 10 characters

    def _get_file_name(self) -> str:
        if not self._addr:
            self._logger.error("_get_file_name: No cell selected")
            raise Exception("No cell selected")
        sheet_id = self._get_sheet_id()
        file_name = f"{self.safe_filename_hash(sheet_id, str(self._addr.Column), str(self._addr.Row))}.py"
        return file_name

    def get_code(self) -> str:
        file_name = self._get_file_name()
        psa = self._doc.python_script
        with contextlib.suppress(Exception):
            return psa.read_file(file_name)
        self._logger.debug(f"get_code: file_name:{file_name} not found")
        return ""

    def save_code(self, code: str) -> None:
        if not self._addr:
            self._logger.error("_get_file_name: No cell selected")
            raise Exception("No cell selected")
        psa = self._doc.python_script
        psa.test_compile_python(code)
        file_name = self._get_file_name()
        self._logger.debug(f"save_code: filename:{file_name}")
        psa.write_file(file_name, code, mode="w")
        self._logger.debug(f"save_code: code saved")

    def _get_sheet_id(self) -> str:
        # need to get a unique id for the sheet.
        # This id will be used to created a name to store the python code.
        if not self._addr:
            self._logger.error("_get_file_name: No cell selected")
            raise Exception("_get_sheet_id() No cell selected")
        try:
            sheet = self._doc.sheets[self._addr.Sheet]
            if len(sheet.draw_page.forms) == 0:
                self._logger.debug("_get_sheet_id: No forms found. Creating a new Form")
                frm = sheet.draw_page.forms.add_form("Form1")
            else:
                self._logger.debug("_get_sheet_id: Form found")
                frm = sheet.draw_page.forms[0]
            if frm.has_by_name(self._hidden_name):
                self._logger.debug("_get_sheet_id: Hidden control found")
                ctl = FormCtlHidden(frm.get_by_name(self._hidden_name), self._doc.lo_inst)
                sheet_id = cast(str, ctl.get_property("sheet_id"))
                self._logger.debug(f"_get_sheet_id: sheet_id:{sheet_id}")
                return sheet_id
            self._logger.debug("_get_sheet_id: Hidden control not found. Creating a new Hidden control")
            ctl = frm.insert_control_hidden(name=self._hidden_name)
            ctl.hidden_value = "SheetId"
            str_id = gUtil.Util.generate_random_string(10)
            ctl.add_property("sheet_id", PropertyAttributeEnum.CONSTRAINED, str_id)
            self._logger.debug(f"_get_sheet_id: returning str_id:{str_id}")
            return str_id
        except Exception as e:
            self._logger.error(f"_get_sheet_id: {e}", exc_info=True)
            raise
