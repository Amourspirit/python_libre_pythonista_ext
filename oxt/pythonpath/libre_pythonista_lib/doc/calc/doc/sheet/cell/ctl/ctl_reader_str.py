from __future__ import annotations

from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing_extensions import override
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import (
        QryCtlOrigRuleName,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import (
        QryCtlModifyTriggerEvent,
    )
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
    from libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_shape_name import QryCtlShapeName
    from libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_rule_name import QryCtlRuleName
    from libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_orig_rule_name import QryCtlOrigRuleName
    from libre_pythonista_lib.cq.query.calc.sheet.cell.ctl.qry_ctl_modify_trigger_event import QryCtlModifyTriggerEvent

    def override(f) -> object:  # noqa: ANN001
        return f


class CtlReaderStr(CtlReader):
    @override
    def append_query(self) -> None:
        self.append(QryCtlShapeName(self.cell, self.ctl))
        self.append(QryCtlRuleName(self.cell, self.ctl))
        self.append(QryCtlOrigRuleName(self.cell, self.ctl))
        self.append(QryCtlModifyTriggerEvent(self.cell, self.ctl))
