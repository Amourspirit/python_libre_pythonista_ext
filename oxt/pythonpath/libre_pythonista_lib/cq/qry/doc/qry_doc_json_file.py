from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result

# tested in tests/test_cmd/test_cmd_lp_doc_json_file.py


class QryDocJsonFile(QryBase, LogMixin, QryCacheT[Result[DocJsonFile, None] | Result[None, Exception]]):
    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SIMPLE_CACHE
        self._doc = doc
        self.root_dir = root_dir
        if ext and not file_name.endswith(ext):
            file_name = f"{file_name}.{ext}"
        self.file_name = file_name

    def execute(self) -> Result[DocJsonFile, None] | Result[None, Exception]:
        """
        Executes the query to get the shared event.

        Returns:
            Result: Success with DocJsonFile or Failure with Exception
        """

        try:
            djf = DocJsonFile(self._doc, self.root_dir)
            if djf.file_exist(self.file_name):
                return Result.success(djf)
            return Result.failure(FileNotFoundError("File does not exist"))
        except Exception as e:
            self.log.exception("Error getting script url")
            return Result.failure(e)

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return f"DocJsonFile_{self.file_name}"
