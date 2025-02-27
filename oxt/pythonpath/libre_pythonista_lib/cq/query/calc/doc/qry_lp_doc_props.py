from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.query.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

else:
    from libre_pythonista_lib.cq.query.qry_base import QryBase
    from libre_pythonista_lib.cq.query.qry_cache_t import QryCacheT
    from libre_pythonista_lib.cq.query.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class QryLpDocProps(QryBase, QryCacheT[dict | None]):
    def __init__(self, doc: CalcDoc) -> None:  # noqa: ANN401
        QryBase.__init__(self)
        self.kind = CalcQryKind.SIMPLE_CACHE
        self._doc = doc
        self._data = cast(dict | None, NULL_OBJ)

    def _get_data(self) -> dict | None:
        qry = QryLpDocJsonFile(self._doc)
        result = self._execute_qry(qry)
        if result is None:
            return None
        return result.read_json(qry.file_name)

    def execute(self) -> Any:  # noqa: ANN401
        if self._data is NULL_OBJ:
            self._data = self._get_data()
        return self._data

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return DOC_LP_DOC_PROP_DATA
