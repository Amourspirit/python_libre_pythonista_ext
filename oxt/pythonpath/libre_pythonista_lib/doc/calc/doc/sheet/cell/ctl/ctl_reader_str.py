from __future__ import annotations

from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import QryCtlOrigRuleName
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
    from libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from libre_pythonista_lib.query.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import QryCtlOrigRuleName


class CtlReaderStr(CtlReader):
    def append_query(self) -> None:
        super().append_query()
        self.append(QryCtlShapeName(self.cell, self.ctl))
        self.append(QryCtlRuleName(self.cell, self.ctl))
        self.append(QryCtlOrigRuleName(self.cell, self.ctl))
