from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
    from oxt.pythonpath.libre_pythonista_lib.cq.query.doc.qry_doc_props import QryDocProps
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
    from libre_pythonista_lib.cq.query.doc.qry_doc_props import QryDocProps
    from libre_pythonista_lib.cq.query.qry_cache_t import QryCacheT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


class QryDocLpProps(QryDocProps, QryCacheT[DocJsonFile | None]):
    def __init__(self, doc: OfficeDocumentT) -> None:
        cfg = BasicConfig()
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        super().__init__(doc=doc, file_name=file_name)
        self.kind = CalcQryKind.SIMPLE_CACHE

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return DOC_LP_PROPERTIES
