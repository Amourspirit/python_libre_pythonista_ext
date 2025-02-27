from __future__ import annotations
from typing import TYPE_CHECKING

from ooodev.io.json.doc_json_file import DocJsonFile

if TYPE_CHECKING:
    from ooodev.proto.office_document_t import OfficeDocumentT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cq.query.qry_t import QryT


class QryDocProps(QryBase, LogMixin, QryT[DocJsonFile | None]):
    def __init__(self, doc: OfficeDocumentT, file_name: str, root_dir: str = "json", ext: str = "json") -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc
        self._root_dir = root_dir
        if ext and not file_name.endswith(ext):
            file_name = f"{file_name}.{ext}"
        self._name = file_name

    def execute(self) -> DocJsonFile | None:
        """
        Executes the query to get the shared event.

        Returns:
            SharedEvent: The shared event or None if an error occurred.
        """

        try:
            djf = DocJsonFile(self._doc, self._root_dir)
            if djf.file_exist(self._name):
                return djf
            return None
        except Exception:
            self.log.exception("Error getting script url")
        return None
