from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture


if __name__ == "__main__":
    pytest.main([__file__])


def test_qry_cell_prop_values(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import (
            QryCellPropValues,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Test with no properties set
        qry = QryCellPropValues(cell=cell, prop_names=[])
        result = qry_handler.handle(qry)
        assert isinstance(result, DotDict)
        assert len(result) == 0

        # Set some custom properties
        cell.set_custom_property("prop1", "value1")
        cell.set_custom_property("prop2", 42)
        cell.set_custom_property("prop3", True)

        # Test getting multiple properties
        qry = QryCellPropValues(cell=cell, prop_names=["prop1", "prop2", "prop3"])
        result = qry_handler.handle(qry)
        assert isinstance(result, DotDict)
        assert result.prop1 == "value1"
        assert result.prop2 == 42
        assert result.prop3 is True

        # Test with non-existent property and default value
        qry = QryCellPropValues(cell=cell, prop_names=["missing", "prop1"], default="default_value")
        result = qry_handler.handle(qry)
        assert result.missing == "default_value"
        assert result.prop1 == "value1"

        # Test cell property access
        assert qry.cell == cell

    finally:
        if doc is not None:
            doc.close(True)


def test_qry_cell_prop_values_error(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.helper.dot_dict import DotDict

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import (
            QryCellPropValues,
        )
        from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory
    else:
        from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_cell_prop_values import QryCellPropValues
        from libre_pythonista_lib.cq.qry.qry_handler_factory import QryHandlerFactory

    doc = None
    try:
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        qry_handler = QryHandlerFactory.get_qry_handler()

        # Mock to simulate an error
        qry = QryCellPropValues(cell=cell, prop_names=["prop1"])
        mocker.patch.object(qry, "_get_prop_value", side_effect=Exception("Simulated error"))

        result = qry_handler.handle(qry)
        assert isinstance(result, DotDict)
        assert len(result) == 0

    finally:
        if doc is not None:
            doc.close(True)
