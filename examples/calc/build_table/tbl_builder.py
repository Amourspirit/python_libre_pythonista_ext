from builder.build_table import BuildTable
from ooodev.utils.lo import Lo
from ooodev.dialog.msgbox import MsgBox, MessageBoxType, MessageBoxButtonsEnum, MessageBoxResultsEnum
from ooodev.macro import MacroLoader


def build_table(*args) -> None:
    with MacroLoader() as loader:
        try:
            bt = BuildTable(im_fnm="", out_fnm="", add_style=False)
            bt.main()
        except Exception as e:
            MsgBox.msgbox(str(e), "error", boxtype=MessageBoxType.ERRORBOX)


def build_table_style(*args) -> None:
    with MacroLoader():
        try:
            bt = BuildTable(im_fnm="", out_fnm="", add_style=True)
            bt.main()
        except Exception as e:
            MsgBox.msgbox(str(e), "error", boxtype=MessageBoxType.ERRORBOX)


def build_table_style_chart(*args) -> None:
    with MacroLoader():
        try:
            bt = BuildTable(im_fnm="", out_fnm="", add_style=True, add_chart=True)
            bt.main()
        except Exception as e:
            MsgBox.msgbox(str(e), "error", boxtype=MessageBoxType.ERRORBOX)


# oooscript compile --embed --config "examples/calc/build_table/config.json" --embed-doc "examples/calc/build_table/builder.ods"
