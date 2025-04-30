from __future__ import annotations
from typing import Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_json_file_del import CmdDocJsonFileDel
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.doc.cmd_doc_json_file_del import CmdDocJsonFileDel


class CmdLpDocJsonFileDel(CmdDocJsonFileDel):
    def __init__(self, doc: OfficeDocumentT) -> None:
        cfg = BasicConfig()
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        CmdDocJsonFileDel.__init__(self, doc=doc, file_name=file_name)
        self.log.debug("init done for doc %s", doc.runtime_uid)
