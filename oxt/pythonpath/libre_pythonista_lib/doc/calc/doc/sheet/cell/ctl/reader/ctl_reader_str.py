from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_shape_base import (
        CtlReaderShapeBase,
    )
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_str import QryStr
    from oxt.pythonpath.libre_pythonista_lib.utils.custom_ext import override
else:
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.reader.ctl_reader_shape_base import CtlReaderShapeBase
    from libre_pythonista_lib.cq.qry.calc.sheet.cell.ctl.read.qry_str import QryStr
    from libre_pythonista_lib.utils.custom_ext import override

# tested in: tests/test_doc/test_calc/test_doc/test_sheet/test_cell/test_ctl/test_ctl_builder_str.py


class CtlReaderStr(CtlReaderShapeBase):
    @override
    def append_query(self) -> None:
        super().append_query()
        self.append(QryStr(self.cell, self.ctl))
