from __future__ import annotations
import pytest
from typing import TYPE_CHECKING


def test_addr_valid(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    else:
        from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    # Test valid address format
    addr = Addr("sheet_index=0&cell_addr=A1")
    assert addr.value == "sheet_index=0&cell_addr=A1"
    assert str(addr) == "sheet_index=0&cell_addr=A1"


def test_addr_invalid(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    else:
        from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    # Test invalid address formats
    with pytest.raises(AssertionError):
        Addr("invalid")

    with pytest.raises(AssertionError):
        Addr("sheet_index=A&cell_addr=A1")

    with pytest.raises(AssertionError):
        Addr("sheet_index=0&cell_addr=11")

    with pytest.raises(AssertionError):
        Addr("sheet_index=0&cell_addr=a1")


def test_addr_equality(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    else:
        from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    addr1 = Addr("sheet_index=0&cell_addr=A1")
    addr2 = Addr("sheet_index=0&cell_addr=A1")
    addr3 = Addr("sheet_index=1&cell_addr=B2")

    # Test equality with same address
    assert addr1 == addr2

    # Test equality with different addresses
    assert addr1 != addr3

    # Test equality with string
    assert addr1 == "sheet_index=0&cell_addr=A1"

    # Test equality with invalid type
    assert addr1 != 123


def test_addr_hash(build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    else:
        from libre_pythonista_lib.data_type.calc.sheet.cell.prop.addr import Addr
    # Test that Addr objects can be used as dictionary keys
    addr1 = Addr("sheet_index=0&cell_addr=A1")
    addr2 = Addr("sheet_index=0&cell_addr=A1")
    addr3 = Addr("sheet_index=1&cell_addr=B2")

    addr_dict = {addr1: "value1"}
    assert addr_dict[addr2] == "value1"  # Should work because addr1 and addr2 are equal

    with pytest.raises(KeyError):
        _ = addr_dict[addr3]  # Should fail because addr3 is different


if __name__ == "__main__":
    pytest.main([__file__])
