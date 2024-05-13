from __future__ import annotations, unicode_literals
import os
import sys
from ooodev.utils.lo import Lo
from ooodev.office.calc import Calc
from ooodev.utils.gui import GUI
from ooodev.conn.connectors import ConnectSocket

# from tbl_builder import build_table_style
import tbl_builder


def main(arg: str = ""):
    os.environ["ODEV_MACRO_LOADER_OVERRIDE"] = "1"
    loader = Lo.load_office(connector=ConnectSocket())
    doc = Calc.create_doc(loader)
    GUI.set_visible(visible=True, doc=doc)
    Lo.delay(300)  # slight delay to allow GUI to appear
    if arg == "style":
        tbl_builder.build_table_style()
    elif arg == "chart":
        tbl_builder.build_table_style_chart()
    else:
        tbl_builder.build_table()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
