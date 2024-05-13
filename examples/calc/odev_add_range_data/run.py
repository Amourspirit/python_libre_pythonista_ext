# The tab dialog uses the ooodev library, therefore, MacroLoader is used to load the library context in the macro methods.
# In this script we don't want the MacroLoader to reset the context, so we set the environment variable ODEV_MACRO_LOADER_OVERRIDE to 1.
#
# Lo.Loader() context manager is used to start LibreOffice and close it when the context manager exits.
from __future__ import annotations, unicode_literals
import os
from ooodev.utils.lo import Lo
from ooodev.office.calc import Calc
from ooodev.utils.gui import GUI
from ooodev.conn.connectors import ConnectSocket
import script


def main(*args, **kwargs):
    # override the macro loader
    os.environ["ODEV_MACRO_LOADER_OVERRIDE"] = "1"
    loader = Lo.load_office(connector=ConnectSocket())
    doc = Calc.create_doc(loader)
    GUI.set_visible(visible=True, doc=doc)
    Lo.delay(300)  # slight delay to allow GUI to appear
    script.fill()


if __name__ == "__main__":
    main()
