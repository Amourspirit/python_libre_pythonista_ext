from __future__ import annotations
from ooodev.write import WriteDoc
from ooodev.utils.color import StandardColor
from ooodev.format.writer.direct.char.font import Font
from ooodev.dialog.msgbox import MsgBox, MessageBoxButtonsEnum, MessageBoxType
from ooodev.format.writer.direct.para.alignment import Alignment


def show_hello(*args) -> None:
    """
    Displays a message box for Hello World
    """
    from ooodev.utils.lo import Lo

    doc = Lo.current_doc
    _ = doc.msgbox(
        "Hello World!",
        "HI",
        boxtype=MessageBoxType.INFOBOX,
        buttons=MessageBoxButtonsEnum.BUTTONS_OK,
    )


def write_hello(*args) -> None:
    """
    Writes Hello World in Bold to a writer document.

    If not a Writer document then a error message is displayed.

    Returns:
        None:
    """
    # for more on formatting Writer documents see,
    # https://python-ooo-dev-tools.readthedocs.io/en/latest/help/writer/format/index.html
    try:
        doc = WriteDoc.from_current_doc()
        cursor = doc.get_cursor()  # type: ignore
        cursor.goto_end()
        al = Alignment().align_center
        ft = Font(size=36, u=True, b=True, color=StandardColor.GREEN_DARK2)
        cursor.append_para(text="Hello World!", styles=[ft, al])
    except Exception as e:
        _ = MsgBox.msgbox(f"This method requires a Writer document.\n{e}")


g_exportedScripts = (show_hello, write_hello)

if __name__ == "__main__":
    show_hello()
