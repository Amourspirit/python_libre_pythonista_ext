from __future__ import annotations

from typing import TYPE_CHECKING
import pytest


if __name__ == "__main__":
    pytest.main([__file__])


def test_cmd_cell_prop(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.utils.null import NULL
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
        from oxt.pythonpath.libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_has_prop import QryCellHasProp
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import (
            QryCellPropValue,
        )
    else:
        from libre_pythonista_lib.utils.null import NULL
        from libre_pythonista_lib.cq.cmd.cmd_handler import CmdHandler
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_set import CmdCellPropSet
        from libre_pythonista_lib.cq.cmd.calc.sheet.cell.prop.cmd_cell_prop_del import CmdCellPropDel
        from libre_pythonista_lib.cq.qry.qry_handler import QryHandler
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_has_prop import QryCellHasProp
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_value import QryCellPropValue

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        cmd_handler = CmdHandler()
        qry_handler = QryHandler()
        prop_name = "test_prop"
        prop_value = "test_value"

        qry_has_prop = QryCellHasProp(cell, prop_name)
        result = qry_handler.handle(qry_has_prop)
        assert result is False

        qry_prop_value = QryCellPropValue(cell=cell, name=prop_name)
        result = qry_handler.handle(qry_prop_value)
        assert result is NULL

        qry_prop_value = QryCellPropValue(cell=cell, name=prop_name, default=None)
        result = qry_handler.handle(qry_prop_value)
        assert result is None

        cmd_set_prop = CmdCellPropSet(cell, prop_name, prop_value)
        cmd_handler.handle(cmd_set_prop)

        result = qry_handler.handle(qry_prop_value)
        assert result == prop_value

        cmd_del_prop = CmdCellPropDel(cell, prop_name)
        cmd_handler.handle(cmd_del_prop)

        qry_prop_value = QryCellPropValue(cell=cell, name=prop_name)
        result = qry_handler.handle(qry_prop_value)
        assert result is NULL

    finally:
        if not doc is None:
            doc.close(True)
