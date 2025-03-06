from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.qry.doc.qry_doc_json_file import QryDocJsonFile


class QryLpDocJsonFile(QryDocJsonFile):
    def __init__(self, doc: OfficeDocumentT) -> None:
        cfg = BasicConfig()
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        super().__init__(doc=doc, file_name=file_name)
