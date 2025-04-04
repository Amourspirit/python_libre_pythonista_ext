from __future__ import annotations

from typing import TYPE_CHECKING, Iterable
from ooodev.utils.helper.dot_dict import DotDict

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.cq.qry.qry_t import QryT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.utils.result import Result
else:
    from libre_pythonista_lib.cq.qry.qry_base import QryBase
    from libre_pythonista_lib.cq.qry.qry_t import QryT
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.utils.result import Result

# tested in: tests/test_cmd/test_cmd_py_src.py


class QryDirectData(QryBase, LogMixin, QryT[Result[Iterable[Iterable[object]], None] | Result[None, Exception]]):
    """Gets the ``data.data`` result value"""

    def __init__(self, data: DotDict) -> None:
        """Constructor

        Args:
            data (DotDict): Data to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._data = data
        self.log.debug("init done")

    def execute(self) -> Result[Iterable[Iterable[object]], None] | Result[None, Exception]:
        """
        Executes the query to get the result.

        Returns:
            Result: Success with result or Failure with Exception
        """
        try:
            return Result.success(((self._data.data,),))
        except Exception as e:
            return Result.failure(e)
