from __future__ import annotations
from typing import Any, Dict, Tuple
import types

from ooodev.calc import CalcSheet
from ..code.py_source_mgr import PySourceManager


class PyModule:

    def __init__(self):

        self.mod = types.ModuleType("PyMod")
        self._init_mod()

    def _init_mod(self) -> None:
        code = """from __future__ import annotations
from typing import Any, cast
from ooodev.calc import CalcDoc
from ooodev.calc import CalcSheet
from ooodev.utils.data_type.cell_obj import CellObj
from ooodev.utils.data_type.range_obj import RangeObj
    """
        exec(code, self.mod.__dict__)
        # setattr(self.mod, "np", np)
        # setattr(self.mod, "Lo", lo)
        # setattr(self.mod, "XSCRIPTCONTEXT", Lo.XSCRIPTCONTEXT)
        # setattr(self.mod, "CalcDoc", CalcDoc)


class PyNode:
    def __init__(self, mod: PyModule, sheet_id: str, cell: Tuple[int, int], next: PyNode | None = None):
        self.cell = cell
        self._mod = mod
        self._mod_dict = self._mod.__dict__.copy()
        self.next = next

    def update_cell(self):
        # get the code for this python cell.
        # run the code in the module and get the result.
        self._mod.__dict__.clear()
        self._mod.__dict__.update(self._mod_dict)
        code = self._mod.sfa.read_text_file(self._uri)
        exec(code, self._mod.__dict__)


class PyLinkedList:
    _instances = {}

    def __new__(cls, sheet: CalcSheet):
        if sheet.unique_id in cls._instances:
            result = cls._instances[sheet.unique_id]
            result._is_init = False
            return result
        return super().__new__(cls)

    def __init__(self, sheet: CalcSheet):
        if self._is_init:
            return
        if sheet.unique_id in self._instances:
            self._instance = self._instances[sheet.unique_id]
        self._mod = PyModule()
        self.head: PyNode | None = None
        self._length = 0
        self._sheet = sheet
        self._sheet_id = sheet.unique_id
        self._is_init = True

    def __len__(self) -> int:
        return self._length

    def insert_at_beginning(self, cell: Tuple[int, int]):
        node = PyNode(self._sheet_id, cell, self.head)
        self.head = node
        self._length += 1
        itr = self.head

        while itr.next:
            itr.update_cell()
            itr = itr.next

    def insert_at_end(self, cell: Tuple[int, int]):
        if self.head is None:
            self.head = PyNode(self._sheet_id, cell, None)
            self.head.update_cell()
            return

        itr = self.head
        while itr.next:
            itr = itr.next

        itr.next = PyNode(sheet_id, cell, None)
        itr.next.update_cell()
        self._length += 1

    def insert_at(self, index, sheet_id: str, cell: Tuple[int, int]):
        if index < 0 or index > len(self):
            raise Exception("Invalid Index")

        if index == 0:
            self.insert_at_beginning(data)
            return

        count = 0
        itr = self.head
        while itr:
            if count == index - 1:
                node = PyNode(data, itr.next)
                itr.next = node
                break

            itr = itr.next
            count += 1
        self._length += 1

    def remove_at(self, index):
        if self.head is None:
            raise Exception("Linked List is empty")
        if index < 0 or index >= len(self):
            raise Exception("Invalid Index")

        if index == 0:
            self.head = self.head.next
            return

        count = 0
        itr = self.head
        while itr:
            if count == index - 1:
                itr.next = itr.next.next  # type: ignore
                break

            itr = itr.next
            count += 1
        self._length -= 1

    def insert_values(self, data_list):
        self.head = None
        for data in data_list:
            self.insert_at_end(data)

    def insert_after_value(self, data_after, data_to_insert):
        if self.head is None:
            return

        if self.head.data == data_after:
            self.head.next = PyNode(data_to_insert, self.head.next)
            self._length += 1
            return

        itr = self.head
        while itr:
            if itr.data == data_after:
                itr.next = PyNode(data_to_insert, itr.next)
                self._length += 1
                break

            itr = itr.next

    def remove_by_value(self, data):
        if self.head is None:
            return

        if self.head.data == data:
            self.head = self.head.next
            return

        itr = self.head
        while itr.next:
            if itr.next.data == data:
                itr.next = itr.next.next
                self._length -= 1
                break
            itr = itr.next


if __name__ == "__main__":
    ll = LinkedList()
    ll.insert_values(["banana", "mango", "grapes", "orange"])
    ll.print()
    ll.insert_after_value("mango", "apple")
    ll.print()
    ll.remove_by_value("orange")
    ll.print()
    ll.remove_by_value("figs")
    ll.print()
    ll.remove_by_value("banana")
    ll.remove_by_value("mango")
    ll.remove_by_value("apple")
    ll.remove_by_value("grapes")
    ll.print()

    # ll.insert_values([45,7,12,567,99])
    # ll.insert_at_end(67)
    # ll.print()
