from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_shape_base import (
        CtlReaderShapeBase,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_int import QryInt
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_shape_base import CtlReaderShapeBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_int import QryInt
    from libre_pythonista_lib.utils.custom_ext import override


class CtlReaderInt(CtlReaderShapeBase):
    @override
    def append_query(self) -> None:
        super().append_query()
        self.append(QryInt(self.cell, self.ctl))
