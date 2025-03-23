from __future__ import annotations
from typing import Any, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
    from libre_pythonista_lib.cq.qry.calc.doc.qry_doc_t import QryDocT
    from libre_pythonista_lib.utils.result import Result

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class QryLpDocProp(QryBase, QryDocT[Any]):
    def __init__(self, doc: CalcDoc, name: str, default: Any = NULL_OBJ) -> None:  # noqa: ANN401
        QryBase.__init__(self)
        self._doc = doc
        self._name = name
        self._default = default

    def _get_data(self) -> dict | None:
        qry = QryLpDocProps(self._doc)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    def execute(self) -> Any:  # noqa: ANN401
        data = self._get_data()
        if data is None:
            return self._default
        return data.get(self._name, self._default)
