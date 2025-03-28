from __future__ import annotations
from typing import Any, TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_cell_item_facade(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
        from libre_pythonista_lib.kind.ctl_kind import CtlKind

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Create facade instance
        facade = CellItemFacade(cell)

        # Test initial state
        assert not facade.is_control()
        assert facade.get_control_kind() == CtlKind.UNKNOWN
        matched_rule = facade.get_matched_rule()
        assert matched_rule is None

        # Test adding default control
        result = facade.add_default_control()
        assert result == (("",),)  # Initially empty string
        assert facade.is_control()
        assert facade.get_control_kind() == CtlKind.STRING

        # Test updating code to float
        test_code = "x = 42.3"
        facade.update_code(test_code)

        # Verify rule matching after adding code
        rule = facade.get_matched_rule()
        assert rule is not None

        # Test getting control
        control = facade.get_control()
        assert control is not None

        control_kind = facade.get_control_kind()
        assert control_kind == CtlKind.FLOAT

        # Test updating code to int
        test_code = "x = 52"
        facade.update_code(test_code)

        # Verify rule matching after adding code
        rule = facade.get_matched_rule()
        assert rule is not None

        # Test getting control
        control = facade.get_control()
        assert control is not None

        control_kind = facade.get_control_kind()
        assert control_kind == CtlKind.INTEGER

    finally:
        if doc is not None:
            doc.close(True)


def test_cell_item_facade_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.cell_item_facade import CellItemFacade

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock CmdCodeName to simulate failure
        mocker.patch(
            "libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_code_name.CmdCodeName.success",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Create facade instance
        facade = CellItemFacade(cell)

        # Test error handling when adding code
        facade.add_default_control()
        assert facade.get_matched_rule() is None

    finally:
        if doc is not None:
            doc.close(True)
