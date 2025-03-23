from __future__ import annotations
from typing import cast, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.const.cache_const import DOC_CALC_PROPS
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_props import QryLpDocProps
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from libre_pythonista_lib.doc_props.calc_props2 import CalcProps2
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.log.log_mixin import LogMixin


# tested in tests/test_cmd_qry/test_doc/test_cmd_calc_props.py


class QryCalcProps(QryBase, LogMixin, QryCacheT[Result[CalcProps2, None] | Result[None, Exception]]):
    """Gets the calc properties"""

    def __init__(self, doc: CalcDoc) -> None:
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self.kind = CalcQryKind.SIMPLE_CACHE
        self._doc = doc

    def _get_data(self) -> dict | None:
        qry = QryLpDocProps(self._doc)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data
        return None

    def execute(self) -> Result[CalcProps2, None] | Result[None, Exception]:
        """
        Executes the query and gets the calc properties.

        Returns:
            Result: Success with calc properties or Failure with Exception
        """
        try:
            data = self._get_data()
            if data is None:
                return Result.success(CalcProps2())
            cp = CalcProps2.from_dict(data)
            return Result.success(cp)
        except Exception as e:
            return Result.failure(e)

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return DOC_CALC_PROPS
