from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_cache_t import QryCacheT
    from libre_pythonista_lib.cq.qry.calc.doc.qry_lp_doc_json_file import QryLpDocJsonFile
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.utils.result import Result
    from libre_pythonista_lib.const.cache_const import DOC_LP_DOC_PROP_DATA

# tested in tests/test_cmd_qry/test_doc/test_cmd_lp_doc_prop.py


class QryLpDocProps(QryBase, QryCacheT[Result[dict, None] | Result[None, Exception]]):
    """
    Query class for retrieving LibrePythonista document properties.

    Inherits from QryBase and QryCacheT with a Result type that can either contain
    a dictionary of properties or an Exception.
    """

    def __init__(self, doc: CalcDoc) -> None:  # noqa: ANN401
        """
        Initialize the query with a CalcDoc instance.

        Args:
            doc: The CalcDoc instance to query properties from
        """
        QryBase.__init__(self)
        self.kind = CalcQryKind.SIMPLE_CACHE
        self._doc = doc

    def _get_data(self) -> dict:
        """
        Retrieves the document properties data from the JSON file.

        Returns:
            dict: The document properties data

        Raises:
            Exception: If the JSON file cannot be read or does not exist
        """
        qry = QryLpDocJsonFile(self._doc)
        result = self._execute_qry(qry)
        if Result.is_success(result):
            return result.data.read_json(qry.file_name)
        raise result.error

    def execute(self) -> Result[dict, None] | Result[None, Exception]:
        """
        Executes the query to get the document properties.

        Returns:
            Result: Success with properties dict or Failure with Exception
        """
        try:
            result = self._get_data()
            return Result.success(result)
        except Exception as e:
            return Result.failure(e)

    @property
    def cache_key(self) -> str:
        """
        Gets the cache key for storing query results.

        Returns:
            str: The cache key constant DOC_LP_DOC_PROP_DATA
        """
        return DOC_LP_DOC_PROP_DATA
