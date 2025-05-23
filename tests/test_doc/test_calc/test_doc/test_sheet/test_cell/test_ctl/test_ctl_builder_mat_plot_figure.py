from __future__ import annotations
from typing import TYPE_CHECKING, cast
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_ctl_builder_mat_plot_figure(loader, build_setup, copy_fix_img, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.color import StandardColor
    from ooodev.units import SizePosMM100

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.kind.ctl_kind import CtlKind
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import (
            get_builder,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import (
            get_reader,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from oxt.___lo_pip___.basic_config import BasicConfig
        from oxt.___lo_pip___.config import Config
        from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config
        from libre_pythonista_lib.utils.result import Result

    doc = None
    try:
        img: Path = copy_fix_img("img_001.svg")

        # patch libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_storage_location.CmdCtlStorageLocation._qry_storage_location() method to return a
        # static path
        mocker.patch(
            "libre_pythonista_lib.cq.cmd.calc.sheet.cell.ctl.cmd_ctl_storage_location.CmdCtlStorageLocation._qry_storage_location",
            return_value=str(img),
        )

        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.MAT_PLT_FIGURE)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"

        ctl_shape_name = f"SHAPE_{config.general_code_name}_cell_{result.ctl_code_name}"
        assert result.ctl_shape_name == ctl_shape_name
        # endregion CtlBuilder

        # region CtlBuilder
        km = KeyMaker()
        assert result.array_ability is False
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is False
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_MP_FIGURE
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_MP_FIGURE)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilder

        reader = get_reader(calc_cell=cell, kind=CtlKind.MAT_PLT_FIGURE)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_MP_FIGURE
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_MP_FIGURE
        assert ctl.ctl_shape_name == result.ctl_shape_name
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.array_ability == result.array_ability

        pos_size = cast(SizePosMM100, ctl.cell_pos_size)
        assert pos_size.x >= 0
        assert pos_size.y >= 0
        assert pos_size.width > 0
        assert pos_size.height > 0
        # end region CtlReaderStr

    finally:
        if doc is not None:
            doc.close(True)
