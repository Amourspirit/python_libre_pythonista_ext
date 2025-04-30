from __future__ import annotations
from typing import TYPE_CHECKING, cast
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_ctl_builder_none(loader, build_setup, mocker: MockerFixture) -> None:
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
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.NONE)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_NONE)

        assert result.array_ability is False
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is False
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_NONE
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_NONE)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = get_reader(calc_cell=cell, kind=CtlKind.NONE)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_NONE
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_NONE
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_NONE
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


def test_ctl_builder_empty(loader, build_setup, mocker: MockerFixture) -> None:
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
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.EMPTY)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_EMPTY)

        assert result.array_ability is False
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is False
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_EMPTY
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_EMPTY)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = get_reader(calc_cell=cell, kind=CtlKind.EMPTY)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_EMPTY
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_EMPTY
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_EMPTY
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


def test_ctl_builder_error(loader, build_setup, mocker: MockerFixture) -> None:
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
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.ERROR)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_ERROR)

        assert result.array_ability is False
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is False
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_ERROR
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_ERROR)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = get_reader(calc_cell=cell, kind=CtlKind.ERROR)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_ERROR
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_ERROR
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_ERROR
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


def test_ctl_builder_str(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.color import StandardColor
    from ooodev.units import SizePosMM100

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import (
            CtlBuilderStr,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_str import CtlReaderStr
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from oxt.___lo_pip___.basic_config import BasicConfig
        from oxt.___lo_pip___.config import Config
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_str import CtlBuilderStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_str import CtlReaderStr
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = CtlBuilderStr(cell=cell)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_STR)

        assert result.array_ability is False
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is False
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_STR
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_STR)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = CtlReaderStr(cell=cell)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_STR
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_STR
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_STR
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


def test_ctl_builder_pd_df(loader, build_setup, mocker: MockerFixture) -> None:
    from ooodev.calc import CalcDoc
    from ooodev.utils.color import StandardColor
    from ooodev.units import SizePosMM100

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_df import (
            CtlBuilderPdDf,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_df import (
            CtlReaderPdDf,
        )
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from oxt.pythonpath.libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from oxt.___lo_pip___.basic_config import BasicConfig
        from oxt.___lo_pip___.config import Config
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.ctl_builder_pd_df import CtlBuilderPdDf
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_pd_df import CtlReaderPdDf
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        mocker.patch("libre_pythonista_lib.cq.qry.general.qry_rr_value.QryRRValue.execute", return_value="DataFrame")

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = CtlBuilderPdDf(cell=cell)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_PD_DF)

        assert result.array_ability is True
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is True
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_PD_DF
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_PD_DF)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = CtlReaderPdDf(cell=cell)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_DF
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_DF
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_PD_DF
        assert ctl.ctl_shape_name == result.ctl_shape_name
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.array_ability == result.array_ability

        pos_size = cast(SizePosMM100, ctl.cell_pos_size)
        assert pos_size.x >= 0
        assert pos_size.y >= 0
        assert pos_size.height > 0
        assert pos_size.width > pos_size.height
        # end region CtlReaderStr

    finally:
        if doc is not None:
            doc.close(True)


def test_ctl_builder_pd_series(loader, build_setup, mocker: MockerFixture) -> None:
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
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        mocker.patch("libre_pythonista_lib.cq.qry.general.qry_rr_value.QryRRValue.execute", return_value="DataSeries")

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.SERIES)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_PD_SERIES)

        assert result.array_ability is True
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is True
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_PD_SERIES
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_PD_SERIES)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = get_reader(calc_cell=cell, kind=CtlKind.SERIES)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_SERIES
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_PD_SERIES
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_PD_SERIES
        assert ctl.ctl_shape_name == result.ctl_shape_name
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.array_ability == result.array_ability

        pos_size = cast(SizePosMM100, ctl.cell_pos_size)
        assert pos_size.x >= 0
        assert pos_size.y >= 0
        assert pos_size.height > 0
        assert pos_size.width > pos_size.height
        # end region CtlReaderStr

    finally:
        if doc is not None:
            doc.close(True)


def test_ctl_builder_data_tbl(loader, build_setup, mocker: MockerFixture) -> None:
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
    else:
        from libre_pythonista_lib.kind.ctl_kind import CtlKind
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.props.key_maker import KeyMaker
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.builder.build_director import get_builder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.read_director import get_reader
        from libre_pythonista_lib.kind.rule_name_kind import RuleNameKind
        from libre_pythonista.basic_config import BasicConfig
        from libre_pythonista.config import Config

    doc = None
    try:
        mock_config = mocker.patch("libre_pythonista_lib.cq.qry.general.qry_is_shared_install.Config", Config)
        _ = mocker.patch("libre_pythonista_lib.sheet.calculate.Config", new_callable=lambda: Config)
        mocker.patch.object(mock_config, "is_shared_installed", False, create=True)

        mocker.patch("libre_pythonista_lib.cq.qry.general.qry_rr_value.QryRRValue.execute", return_value="DataTable")

        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]
        # pythonpath.libre_pythonista_lib.cq.qry.general.qry_is_shared_install

        # Create command instance
        builder = get_builder(calc_cell=cell, ctl_kind=CtlKind.DATA_TABLE)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        # region CtlBuilder
        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"
        assert result.ctl_shape_name == f"SHAPE_{result.ctl_name}"
        # endregion CtlBuilder

        # region CtlBuilderStr
        km = KeyMaker()
        assert cell.has_custom_property(km.ctl_orig_ctl_key)
        assert cell.get_custom_property(km.ctl_orig_ctl_key) == str(RuleNameKind.CELL_DATA_TYPE_TBL_DATA)

        assert result.array_ability is True
        assert cell.has_custom_property(km.cell_array_ability_key)
        assert cell.get_custom_property(km.cell_array_ability_key) is True
        assert result.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_TBL_DATA
        assert cell.has_custom_property(km.modify_trigger_event)
        assert cell.get_custom_property(km.modify_trigger_event) == str(RuleNameKind.CELL_DATA_TYPE_TBL_DATA)

        assert cell.has_custom_property(km.ctl_shape_key)
        assert cell.get_custom_property(km.ctl_shape_key) == result.ctl_shape_name
        # endregion CtlBuilderStr

        reader = get_reader(calc_cell=cell, kind=CtlKind.DATA_TABLE)
        ctl = reader.read()
        # region CtlReader
        assert ctl.cell == cell
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

        # end region CtlReader

        # region CtlReaderStr
        assert ctl.ctl_bg_color == StandardColor.TEAL_LIGHT3
        assert ctl.ctl_rule_kind == RuleNameKind.CELL_DATA_TYPE_TBL_DATA
        assert ctl.ctl_orig_rule_kind == RuleNameKind.CELL_DATA_TYPE_TBL_DATA
        assert ctl.modify_trigger_event == RuleNameKind.CELL_DATA_TYPE_TBL_DATA
        assert ctl.ctl_shape_name == result.ctl_shape_name
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.array_ability == result.array_ability

        pos_size = cast(SizePosMM100, ctl.cell_pos_size)
        assert pos_size.x >= 0
        assert pos_size.y >= 0
        assert pos_size.height > 0
        assert pos_size.width > pos_size.height
        # end region CtlReaderStr

    finally:
        if doc is not None:
            doc.close(True)
