from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_props_del import CmdDocPropsDel
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.doc.cmd_doc_props_del import CmdDocPropsDel


class CmdDocLpPropsDel(CmdDocPropsDel):
    def __init__(self, doc: OfficeDocumentT) -> None:
        cfg = BasicConfig()
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        CmdDocPropsDel.__init__(self, doc=doc, file_name=file_name)
