from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.doc.cmd_doc_props import CmdDocProps
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
    from oxt.pythonpath.libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cq.cmd.doc.cmd_doc_props import CmdDocProps
    from libre_pythonista_lib.const.cache_const import DOC_LP_PROPERTIES
    from libre_pythonista_lib.cq.cmd.cmd_cache_t import CmdCacheT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdDocLpProps(CmdDocProps, CmdCacheT):
    def __init__(self, doc: OfficeDocumentT) -> None:
        cfg = BasicConfig()
        file_name = f"{cfg.general_code_name}{cfg.calc_props_json_name}"
        CmdDocProps.__init__(self, doc=doc, file_name=file_name)
        self.kind = CalcCmdKind.SIMPLE_CACHE

    @property
    def cache_keys(self) -> Tuple[str, ...]:
        return (DOC_LP_PROPERTIES,)
