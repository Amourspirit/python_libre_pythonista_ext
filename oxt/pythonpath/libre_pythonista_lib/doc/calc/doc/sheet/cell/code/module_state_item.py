from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from ooodev.utils.data_type.cell_obj import CellObj
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.code.py_module_state import PyModuleState
else:
    PyModuleState = Any


class ModuleStateItem:
    def __init__(self, cell_obj: CellObj, mod_dict: Dict[str, Any], owner: PyModuleState) -> None:
        self.cell_obj = cell_obj.copy()
        self.mod_dict = mod_dict
        self.py_state = owner
        self.dd_data = DotDict(
            data=self.mod_dict.get("_"), cell_obj=cell_obj.copy(), runtime_uid=self.py_state.runtime_uid
        )

    def __lt__(self, other: object) -> bool:
        """
        Enables sorting ModuleStateItem objects by cell_obj.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if self is less than other, False otherwise
        """
        if isinstance(other, ModuleStateItem):
            return self.cell_obj < other.cell_obj
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        """
        Enables sorting ModuleStateItem objects by cell_obj.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if self is greater than other, False otherwise
        """
        if isinstance(other, ModuleStateItem):
            return self.cell_obj > other.cell_obj
        return NotImplemented

    def __le__(self, other: object) -> bool:
        """
        Enables sorting ModuleStateItem objects by cell_obj.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if self is less than or equal to other, False otherwise
        """
        if isinstance(other, ModuleStateItem):
            return self.cell_obj <= other.cell_obj
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        """
        Enables sorting ModuleStateItem objects by cell_obj.

        Args:
            other (Any): Object to compare with

        Returns:
            bool: True if self is greater than or equal to other, False otherwise
        """
        if isinstance(other, ModuleStateItem):
            return self.cell_obj >= other.cell_obj
        return NotImplemented

    def __repr__(self) -> str:
        return f"<ModuleStateItem({self.cell_obj})>"

    def __str__(self) -> str:
        return f"<ModuleStateItem({self.cell_obj})>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ModuleStateItem):
            return self.cell_obj == other.cell_obj
        return NotImplemented
