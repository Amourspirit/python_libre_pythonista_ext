from __future__ import annotations
from ooodev.utils.lo import Lo
from ooodev.utils.gui import GUI, ZoomKind
from ooodev.office.write import Write
from ooodev.utils.color import StandardColor
from ooodev.format.writer.direct.char.font import Font
from ooodev.dialog.msgbox import MsgBox, MessageBoxButtonsEnum, MessageBoxType, MessageBoxResultsEnum
from ooodev.format.writer.direct.para.alignment import Alignment


def write_hello(show_msg: bool = True) -> None:
    """
    Writes Hello World in Bold to a writer document.

    If not a Writer document then a error message is displayed.

    Returns:
        None:
    """
    # for more on formatting Writer documents see,
    # https://python-ooo-dev-tools.readthedocs.io/en/latest/help/writer/format/index.html

    # Load LibreOffice Office
    _ = Lo.load_office(Lo.ConnectSocket())
    try:
        doc = Write.create_doc()
        GUI.set_visible(visible=True, doc=doc)
        # a little delay of 300 ms to ensure the zoom dispatch as time to take effect
        Lo.delay(300)
        GUI.zoom(view=ZoomKind.PAGE_WIDTH)

        cursor = Write.get_cursor(doc)
        cursor.gotoEnd(False)
        # create alignment formatting
        al = Alignment().align_center
        # create font formatting
        ft = Font(size=36, u=True, b=True, color=StandardColor.GREEN_DARK2)
        Write.append_para(cursor=cursor, text="Hello World!", styles=[ft, al])
        if show_msg:
            msg_result = MsgBox.msgbox(
                "Do you wish to close document?",
                "All done",
                boxtype=MessageBoxType.QUERYBOX,
                buttons=MessageBoxButtonsEnum.BUTTONS_YES_NO,
            )
            if msg_result == MessageBoxResultsEnum.YES:
                Lo.close_doc(doc=doc, deliver_ownership=True)
                Lo.close_office()
            else:
                print("Keeping document open")
        else:
            return
    except Exception as e:
        Lo.close_office()
        raise


if __name__ == "__main__":
    write_hello()
