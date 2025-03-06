from __future__ import annotations

from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

from ooodev.calc import CalcDoc

if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_shape(loader, build_setup) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import CmdShapeDel
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import CmdShapeDel

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        qry = QryShape(cell=cell)

        # Test empty name (should fail)
        cmd = CmdShape(cell=cell, name="")
        cmd_handler.handle(cmd)
        assert not cmd.success

        # Test setting new shape
        test_name = "SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf"
        cmd = CmdShape(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success

        # Verify the shape was set
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test setting same shape (should succeed but not change anything)
        cmd = CmdShape(cell=cell, name=test_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test changing to different shape and then undoing
        new_name = "SHAPE_libre_pythonista_ctl_cell_id_lfjdlkj35lf"
        cmd = CmdShape(cell=cell, name=new_name)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == new_name

        # Test undo
        cmd.undo()
        result = qry_handler.handle(qry)
        assert result == test_name

        # Test deleting the shape
        cmd = CmdShapeDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

        # Test deleting when cell does not have property
        cmd = CmdShapeDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)

        # Test deleting the shape
        cmd = CmdShapeDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)
        assert result == ""

        # Test deleting when cell does not have property
        cmd = CmdShapeDel(cell=cell)
        cmd_handler.handle(cmd)
        assert cmd.success
        result = qry_handler.handle(qry)

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_shape_error_handling(loader, build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Mock execute to raise an exception
        mocker.patch(
            "libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set.CmdCellPropSet.execute",
            side_effect=Exception("Test exception"),
        )

        cmd = CmdShape(cell=cell, name="SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf")
        cmd.execute()
        assert not cmd.success

    finally:
        if doc is not None:
            doc.close(True)


def test_cmd_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape import CmdShape
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    mocker.patch.object(CmdShape, "_get_current_state", return_value="")

    cmd = CmdShape(cell=cell, name="SHAPE_libre_pythonista_ctl_cell_id_l6fiSBIiNVcncf")
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_cmd_del_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import CmdShapeDel
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    else:
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_shape_del import CmdShapeDel
        from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind

    cell = mocker.MagicMock()

    cmd = CmdShapeDel(cell=cell)
    assert cmd.kind == CalcCmdKind.CELL

    cmd.kind = CalcCmdKind.SHEET
    assert cmd.kind == CalcCmdKind.SHEET


def test_qry_kind(build_setup, mocker: MockerFixture) -> None:
    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape
    else:
        from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_shape import QryShape

    cell = mocker.MagicMock()

    qry = QryShape(cell=cell)
    assert qry.kind == CalcQryKind.CELL

    qry.kind = CalcQryKind.SHEET
    assert qry.kind == CalcQryKind.SHEET
