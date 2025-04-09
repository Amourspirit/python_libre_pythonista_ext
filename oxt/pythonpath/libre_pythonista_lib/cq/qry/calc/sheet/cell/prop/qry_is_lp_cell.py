from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_has_code_name import QryHasCodeName
else:
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.prop.qry_has_code_name import QryHasCodeName


class QryIsLpCell(QryHasCodeName):
    """Checks if the cell is a LibrePythonista cell"""
