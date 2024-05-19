from __future__ import annotations

from typing import TYPE_CHECKING
import logging
from ooodev.calc import CalcDoc
from ooodev.loader.inst.options import Options
from ooodev.loader import Lo
from py.dialog_python import DialogPython

# https://gitlab.com/jmzambon/apso/-/blob/master/console/console.py#L283


def main():
    with Lo.Loader(connector=Lo.ConnectSocket(), opt=Options(log_level=logging.DEBUG)):
        doc = CalcDoc.create_doc(visible=True)

        dlg = DialogPython()
        dlg.show()
        doc.close()


if __name__ == "__main__":
    main()
